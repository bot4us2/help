import os
import json
import smtplib
from datetime import datetime
from email.message import EmailMessage
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG SHEET ---
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
HISTORICO_SHEET = "Historico de Emails"  # sem acento
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais_bot.json")
GMAIL_USER = "notificacoes.4us@gmail.com"
GMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD")  # senha de aplicação gerada no Gmail

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
    def enviar_para(dest):
        status = "Falha"
        try:
            msg = EmailMessage()
            msg["Subject"] = assunto
            msg["From"] = GMAIL_USER
            msg["To"] = dest
            msg.set_content(corpo)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_USER, GMAIL_PASS)
                smtp.send_message(msg)
                status = "Enviado (SMTP)"
                print(f"✅ Email enviado para {dest}")
        except Exception as e:
            print(f"❌ Erro ao enviar email para {dest}: {e}")
            status = f"Erro: {e}"

        # --- REGISTAR NO HISTÓRICO ---
        try:
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            linha = [[data_hora, dest, username or "", assunto, motivo, status]]
            sheet.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{HISTORICO_SHEET}!A1",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": linha}
            ).execute()
            print(f"📝 Registo adicionado ao histórico ({dest})")
        except Exception as e:
            print(f"⚠️ Erro ao registar no histórico para {dest}: {e}")

        return status.startswith("Enviado")

    # Envia para o destinatário principal
    resultado_1 = enviar_para(destinatario)

    # Envia também para a equipa (cópia interna)
    resultado_2 = enviar_para("info.fantastic.four@gmail.com")

    return resultado_1 and resultado_2

# --- TESTE LOCAL ---
#if __name__ == "__main__":
 #   enviar_email(
  #      destinatario="notificacoes.4us@gmail.com",
   #     assunto="📧 Teste SMTP via Gmail",
    #    corpo="Este é um teste de envio automático com registo.",
     #   username="teste",
      #  motivo="Teste local"
   # )
