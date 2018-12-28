from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_mail import Mail
from flask_login import LoginManager

db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
ckeditor = CKEditor()
mail = Mail()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
