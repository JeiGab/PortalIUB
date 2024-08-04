import os
import json
import mysql.connector as sql
import bcrypt
from datetime import datetime  
from dotenv import load_dotenv


load_dotenv()


DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': int(os.getenv('DB_PORT'))
}

try:
    conn = sql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    row = cursor.fetchone()
    print("Conexión exitosa a la base de datos.")
    conn.close()
except Exception as e:
    print("Error al conectar a la base de datos.")


def get_database_connection():
    try:
        conn = sql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def update_password(user_id, new_password):
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET password = %s 
                WHERE id = %s
            """, (new_password, user_id))
            conn.commit()
            conn.close()
            print("Contraseña actualizada correctamente.")
            return True
        else:
            print("Error: No se pudo conectar a la base de datos.")
            return False
    except Exception as e:
        print("Error al actualizar la contraseña:", e)
        return False

# Función para validar las credenciales de inicio de sesión
def validate_login(correo, password):
    conn = get_database_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, password FROM users WHERE correo = %s", (correo,))
        user = cursor.fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            return {'id': user[0], 'first_name': user[1], 'last_name': user[2]}
    return None

# Función para verificar si el correo ya está registrado
def email_exists(correo):
    conn = get_database_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE correo = %s", (correo,))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    return False

# Función para insertar datos en la tabla 'users'
def InsertInTable_U(datos):
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (correo, password, first_name, last_name, program) 
                VALUES (%s, %s, %s, %s, %s)
            """, datos)
            conn.commit()
            conn.close()
            print("Datos insertados correctamente.")
            return True
        else:
            print("Error: No se pudo conectar a la base de datos normal.")
            return False
    except Exception as e:
        print("Error al insertar datos:", e)
        return False

# Función para insertar una observación en la tabla 'observations'
def insert_observation(user_id, observation):
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET observaciones = %s 
                WHERE id = %s
            """, (observation, user_id))
            conn.commit()
            conn.close()
            print("Observación insertada correctamente.")
            return True
        else:
            print("Error: No se pudo conectar a la base de datos por observaciones.")
            return False
    except Exception as e:
        print("Error al insertar la observación:", e)
        return False

def log_interaction(user_id, user_message, bot_response, timestamp):
    try:
        conn = get_database_connection()
        if conn:
            cursor = conn.cursor()
            
            # Convertir bot_response a cadena si es un diccionario
            if isinstance(bot_response, dict):
                bot_response = json.dumps(bot_response)
            elif not isinstance(bot_response, str):
                bot_response = str(bot_response)

            cursor.execute("""
                INSERT INTO interactions (user_id, user_message, bot_response, timestamp) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, user_message, bot_response, timestamp))
            conn.commit()
            conn.close()
            print("Interacción registrada correctamente.")
            return True
        else:
            print("Error: No se pudo conectar a la base de datos.")
            return False
    except Exception as e:
        print("Error al registrar la interacción:", e)
        return False
    
