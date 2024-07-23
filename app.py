from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
import os
import bcrypt
from dotenv import load_dotenv
import mysql.connector as sql
from database import get_database_connection, validate_login, email_exists, hash_password, InsertInTable_U, update_password, insert_observation
from dialogflow_bot import detect_intent_texts, SERVICE_ACCOUNT_FILE, PROJECT_ID

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para la sesión

# Ruta principal del chat
@app.route('/')
def index():
    return render_template('index.html')

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

# Ruta para el formulario de inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        # Validar las credenciales de inicio de sesión
        user = validate_login(correo, password)

        if user:
            session['user_id'] = user['id']  # Almacena el ID del usuario en la sesión
            return redirect(url_for('post_login'))
        else:
            flash('Credenciales incorrectas', 'error')

    return render_template('index.html')

# Ruta para la página post-login
@app.route('/post-login')
def post_login():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('post-login.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Eliminar el ID del usuario de la sesión
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('index'))

# Ruta para el formulario de registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        first_name = request.form['first_name']
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
        if InsertInTable_U((correo, hashed_password.decode('utf-8'), first_name, program)):
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

@app.route('/recomends', methods=['GET', 'POST'])
def recomends():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para enviar una observación', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
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
