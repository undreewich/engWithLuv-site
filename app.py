from flask import Flask


from src.app.accessManager import permissionCheckAdmin, permissionCheckStudent
from src.app.mailService import mail
import src.app.config as config

from src.app.bps.usr_bp import usr_bp
from src.app.bps.main_bp import main_bp
from src.app.bps.admin_bp import admin_bp
# from src.app.bps.lesson_bp import lesson_bp
# from src.app.bps.callbacksAPI_bp import callbacksAPI_bp


app = Flask(__name__, template_folder='src/templates', static_folder='src/static')


app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_USE_TLS'] = config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = config.MAIL_USE_SSL
app.config['MAIL_DEFAULT_SENDER'] = (config.MAIL_SENDER_NAME, config.MAIL_SENDER)
app.config['SECRET_KEY'] = config.REGI_SECRET_KEY
mail.init_app(app)



usr_bp.before_request(permissionCheckStudent)
admin_bp.before_request(permissionCheckAdmin)

app.register_blueprint(main_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(usr_bp, url_prefix='/student')
# app.register_blueprint(lesson_bp, url_prefix='/lesson')
# app.register_blueprint(callbacksAPI_bp, url_prefix='/api')
