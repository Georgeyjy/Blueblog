import os

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.extensions import db, moment, bootstrap, ckeditor, mail, login_manager, csrf
from bluelog.settings import config
from bluelog.models import Admin, Category, Comment, Link


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    app.config.from_object(config[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_template_context(app)
    register_errors(app)
    register_commands(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def register_blueprints(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(blog_bp)


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop')
    def initdb(drop):
        if drop:
            click.confirm('Confirm to delete the database?', abort=True)
            db.drop_all()
            click.echo('Deleted database')
        db.create_all()
        click.echo('Initialized database')

    @app.cli.command()
    @click.option('--username', prompt=True, help='Admin username')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='Admin password')
    def create_admin(username, password):
        admin = Admin.query.first()
        if admin:
            click.echo('The administrator exists, updating...')
            admin.username = username
            admin.set_password(password)
        click.echo('Creating admin account...')
        admin = Admin(
            username=username,
            blog_title='A blog',
            blog_subtitle='hakuna matata',
            name='Timon',
            about='Lion king baby'
        )
        admin.password_hash = admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo('Done')

    @app.cli.command()
    @click.option('--category', default=10)
    @click.option('--post', default=50)
    @click.option('--comment', default=500)
    def forge(category, post, comment):
        """Generate fake information"""
        from bluelog.fakes import fake_admin, fake_category, fake_post, fake_comments

        db.drop_all()
        db.create_all()

        click.echo('Generating fake admin...')
        fake_admin()

        click.echo('Generating %d fake categories...' % category)
        fake_category(category)

        click.echo('Generating %d fake posts...' % post)
        fake_post(post)

        click.echo('Generating %d fake comments...' % comment)
        fake_comments(comment)

        click.echo('Done.')
