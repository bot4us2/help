import os
import json
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG SHEET ---
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
HISTORICO_SHEET = "Historico de Emails"
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais_bot.json")

# --- AUTENTICAÇÃO GOOGLE SHEETS ---
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

# --- FUNÇÃO DE ENVIO E REGISTO ---
def enviar_email(destinatario, assunto, corpo, username=None, motivo="N/A"):
    status = "Falha"
    try:
        message = Mail(
            from_email='notificacoes.4us@gmail.com',
            to_emails=destinatario,
            subject=assunto,
            plain_text_content=corpo
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        status = f"Enviado ({response.status_code})"
        print(f"✅ Email enviado via SendGrid: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar com SendGrid: {e}")
        status = f"Erro: {e}"

    # --- REGISTAR NA SHEET ---
    try:
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        linha = [[data_hora, destinatario, username or "", assunto, motivo, status]]
        sheet.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{HISTORICO_SHEET}!A1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": linha}
        ).execute()
        print(f"📝 Registo adicionado ao histórico.")
    except Exception as e:
        print(f"⚠️ Erro ao registar no histórico: {e}")

    return status.startswith("Enviado")
