from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_mail import Mail

db = SQLAlchemy()
moment = Moment()
bootstrap = Bootstrap()
ckeditor = CKEditor()
mail = Mail()
