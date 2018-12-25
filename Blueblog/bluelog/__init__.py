import os

import click
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_mail import Mail

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.blueprints.blog import blog_bp


app = Flask('blueblog')
app.config.from_pyfile('settings.py')

db = SQLAlchemy(app)
moment = Moment(app)
bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)
mail = Mail(app)

app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(blog_bp)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db)


@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop')
def initdb(drop):
    if drop:
        click.confirm('Confirm to delete the database?', abort=True)
        db.drop_all()
        click.echo('Deleted database')
    db.create_all()
    click.echo('Initialized database')
