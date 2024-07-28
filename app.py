from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import os
import bcrypt
from flask_mail import Mail
from dotenv import load_dotenv
import mysql.connector as sql
from email_utils import send_reset_email, verify_reset_token
from database import get_database_connection, validate_login, email_exists, hash_password, InsertInTable_U, update_password, insert_observation
from dialogflow_bot import detect_intent_texts, SERVICE_ACCOUNT_FILE, PROJECT_ID

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  
mail = Mail(app)


class User:
    def __init__(self, id, correo, password, first_name, last_name, program):
        self.id = id
        self.correo = correo
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.program = program

    @staticmethod
    def get_by_email(correo):
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE correo = %s", (correo,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                return User(**user_data)
        return None

    @staticmethod
    def get_by_id(user_id):
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                return User(**user_data)
        return None
    
# Ruta principal del chat
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para el login (GET)
@app.route('/login', methods=['GET'])
def login_form():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    correo = request.form['correo']
    password = request.form['password']

    # Validar las credenciales de inicio de sesión
    user = validate_login(correo, password)

    if user:
        session['user_id'] = user['id']
        session['first_name'] = user['first_name']
        session['last_name'] = user['last_name']
        return redirect(url_for('post_login'))
    else:
        flash('Credenciales incorrectas', 'error')

    return render_template('login.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    if SERVICE_ACCOUNT_FILE:
        message = request.form['messageInput']
        session_id = 'unique_session_id'
        texts = [message]
        language_code = 'es'
        responses = detect_intent_texts(PROJECT_ID, session_id, texts, language_code)
        fulfillment_messages = []
        for response in responses:
            query_result = response.get('queryResult', {})
            if 'fulfillmentMessages' in query_result:
                fulfillment_messages.extend(query_result['fulfillmentMessages'])
        result = []
        for message in fulfillment_messages:
            if 'text' in message:
                result.append(message['text']['text'][0])
            elif 'payload' in message:
                result.append(message['payload'])
        return jsonify({'response': result})
    else:
        message = request.form['messageInput']
        return jsonify({'response': f'Mensaje recibido: {message}'})

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        correo = request.form['correo']
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT correo FROM users WHERE correo = %s", (correo,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                if send_reset_email(user['correo']):
                    flash('Se ha enviado un correo electrónico con las instrucciones para restablecer tu contraseña.', 'info')
                else:
                    flash('Error al enviar el correo electrónico. Por favor, intenta de nuevo más tarde.', 'error')
            else:
                flash('No se encontró ninguna cuenta con ese correo electrónico.', 'error')
        else:
            flash('Error al conectar a la base de datos.', 'error')
        
        return redirect(url_for('forgot_password'))
    
    return render_template('forgot-password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        if password:
            hashed_password = hash_password(password) 
            conn = get_database_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE users SET password = %s WHERE correo = %s", (hashed_password, email))
                    conn.commit()
                    flash('Tu contraseña ha sido actualizada con éxito.', 'success')
                    return redirect(url_for('login'))
                except sql.Error as e:
                    flash(f'Error al actualizar la contraseña: {e}', 'error')
                finally:
                    cursor.close()
                    conn.close()
            else:
                flash('Error al conectar a la base de datos.', 'error')
        else:
            flash('Por favor, ingresa una nueva contraseña.', 'error')
    
    return render_template('reset-password.html', token=token)
    

# Ruta para la página post-login
@app.route('/post-login')
def post_login():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('post-login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        program = request.form['program']

        # Verificar si el correo ya está registrado
        if email_exists(correo):
            flash('El correo ya está registrado', 'error')
            return redirect(url_for('register'))
        
        # Validar el correo
        if not correo.endswith('@unibarranquilla.edu.co'):
            flash('El correo debe ser el correo institucional de la IUB', 'error')
            return redirect(url_for('register'))

        # Validar la contraseña
        if len(password) < 6 or len(password) > 12:
            flash('La contraseña debe tener entre 6 y 12 caracteres.', 'error')
            return redirect(url_for('register'))

        # Encriptar la contraseña
        hashed_password = hash_password(password)

        # Llamar a la función para insertar usuario en la base de datos
        if InsertInTable_U((correo, hashed_password.decode('utf-8'), first_name, last_name, program)):
            flash('Usuario registrado exitosamente', 'success')
        else:
            flash('Error al registrar usuario', 'error')

    return render_template('register.html')

# Ruta para verificar si el correo ya está registrado
@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.get_json()
    correo = data['correo']
    exists = email_exists(correo)
    return jsonify({'exists': exists})

# Ruta para mostrar el formulario de observaciones
@app.route('/recomends', methods=['GET'])
def recomends_form():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para enviar una observación', 'error')
        return redirect(url_for('index'))
    
    return render_template('recomends.html')

@app.route('/recomends', methods=['POST'])
def recomends():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para enviar una observación', 'error')
        return redirect(url_for('index'))

    message = request.form['message']

    if not message:
        flash('El mensaje no puede estar vacío', 'error')
    else:
        user_id = session.get('user_id')

        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO observations (user_id, message) VALUES (%s, %s)", (user_id, message))
                conn.commit()
                flash('Observación enviada correctamente', 'success')
            except sql.Error as e:
                flash(f'Error al enviar la observación: {e}', 'error')
            finally:
                cursor.close()
                conn.close()
        else:
            flash('Error al conectar a la base de datos', 'error')

    return render_template('recomends.html')

# Ruta para mostrar la página de cambio de contraseña
@app.route('/change-password', methods=['GET'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('change-password.html')

# Ruta para procesar el formulario de cambio de contraseña
@app.route('/change_password', methods=['POST'])
def change_password_process():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    user_id = session.get('user_id')

    conn = get_database_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            flash('Usuario no encontrado', 'error')
            return redirect(url_for('change_password'))

        # Verificar la contraseña actual
        if not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
            flash('Contraseña actual incorrecta', 'error')
            return redirect(url_for('change_password'))

        # Validar la nueva contraseña
        if len(new_password) < 6 or len(new_password) > 12:
            flash('La nueva contraseña debe tener entre 6 y 12 caracteres.', 'error')
            return redirect(url_for('change_password'))

        # Verificar si la nueva contraseña y la confirmación coinciden
        if new_password != confirm_password:
            flash('Las contraseñas nuevas no coinciden.', 'error')
            return redirect(url_for('change_password'))

        # Encriptar la nueva contraseña
        hashed_password = hash_password(new_password)

        # Actualizar la contraseña en la base de datos
        if update_password(user_id, hashed_password.decode('utf-8')):
            flash('Contraseña cambiada exitosamente', 'success')
        else:
            flash('Error al cambiar la contraseña', 'error')

    else:
        flash('Error al conectar a la base de datos', 'error')

    return redirect(url_for('change_password'))

# Ejecutar la aplicación Flask
if __name__ == '__main__':
    app.run(debug=True)
