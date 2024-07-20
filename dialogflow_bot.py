# dialogflow_bot.py

import os
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Función para cargar la ruta del archivo de credenciales
def get_service_account_file_path():
    try:
        json_file_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        print(f"Ruta absoluta del archivo JSON: {json_file_path}")  # Imprimir la ruta absoluta
        
        # Comprobar si el archivo existe y es accesible
        if os.path.isfile(json_file_path):
            print("El archivo JSON existe y es accesible.")
            return json_file_path
        else:
            raise FileNotFoundError(f"Error: No se encontró el archivo JSON en {json_file_path}")
    except Exception as e:
        print(f"Error al obtener la ruta del archivo JSON: {str(e)}")
        return None

# Ruta al archivo de credenciales de la cuenta de servicio
SERVICE_ACCOUNT_FILE = get_service_account_file_path()

if SERVICE_ACCOUNT_FILE:
    # Identificador del proyecto de Dialogflow
    PROJECT_ID = 'mani-avls'

    # Configuración de las credenciales de la cuenta de servicio
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    # Función para interactuar con Dialogflow
    def detect_intent_texts(project_id, session_id, texts, language_code):
        session = requests.Session()

        # URL de la API de Dialogflow
        url = f'https://dialogflow.googleapis.com/v2/projects/{project_id}/agent/sessions/{session_id}:detectIntent'

        # Asegúrate de que las credenciales están actualizadas
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

        headers = {
            'Authorization': f'Bearer {credentials.token}',
            'Content-Type': 'application/json'
        }

        responses = []
        for text in texts:
            body = {
                "query_input": {
                    "text": {
                        "text": text,
                        "language_code": language_code
                    }
                }
            }

            response = session.post(url, headers=headers, json=body, verify=False)
            response.raise_for_status()
            responses.append(response.json())

        return responses
