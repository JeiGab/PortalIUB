import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, current_app
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configuración del servidor SMTP
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('MAIL_USERNAME')
SMTP_PASSWORD = os.getenv('MAIL_PASSWORD')
SENDER_EMAIL = os.getenv('MAIL_USERNAME')

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


def send_reset_email(email):
    token = generate_reset_token(email)
    link = url_for('reset_password', token=token, _external=True)
    body = f'''Para restablecer tu contraseña, visita el siguiente enlace:
{link}
Si no hiciste esta solicitud, simplemente ignora este correo electrónico.
'''

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = 'Restablecer tu contraseña'
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True  # El correo se envió correctamente
    except smtplib.SMTPException as e:
        print(f'SMTP Error: {str(e)}')  # Registro específico para errores SMTP
        return False
    except Exception as e:
        print(f'Error general: {str(e)}')  # Registro general de errores
        return False