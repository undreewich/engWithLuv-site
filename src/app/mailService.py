from flask import config, url_for
from flask_mail import Message, Mail

mail = Mail()

def sendRegistrationConfirmationEmail(email, token):
    msg = Message(
        subject='Подтвердите ваш email',
        recipients=[email])
    msg.body = f'Пожалуйста, подтвердите ваш email, перейдя по следующей ссылке: {url_for('main.confirm_email', token=token, _external=True)}'
    mail.send(msg)