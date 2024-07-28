from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, current_app
from app import mail  

def generate_reset_token(email, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expires_sec=1800):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
    except:
        return None
    return email

def send_reset_email(user):
    token = generate_reset_token(user.email)
    msg = Message('Restablecer tu contraseña', 
                  sender='noreply@demo.com', 
                  recipients=[user.email])
    link = url_for('reset_token', token=token, _external=True)
    msg.body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{link}
Si no hiciste esta solicitud, simplemente ignora este correo electrónico.
'''
    mail.send(msg)
