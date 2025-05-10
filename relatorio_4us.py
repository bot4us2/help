import os
import json
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from email_utils import enviar_email  # ✅ função com registo incluído

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_CLIENTES", "Tabela de Clientes 2")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credenciais_bot.json")
DESTINATARIO_RELATORIO = "luis.phoenix@tutanota.com"

# --- Autenticação Google Sheets ---
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

# --- Período do relatório ---
hoje = datetime.now()
inicio_semana = hoje - timedelta(days=hoje.weekday())

# --- Leitura da Sheet ---
result = sheet.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
valores = result.get("values", [])
headers = valores[0]
rows = valores[1:]

idx = lambda nome: headers.index(nome)

renovadas = []
expiradas = []
emails_enviados = []
soma_total = 0

for row in rows:
    row += [""] * (len(headers) - len(row))

    data_sim = row[idx("renovada_no_painel_e_tabela_de_clientes")].strip().upper()
    dias = row[idx("dias_para_terminar")].strip()
    aviso = row[idx("aviso_renovacao_enviado")].strip()
    total = row[idx("total")] if "total" in headers else "0"
    username = row[idx("username")]
    email = row[idx("email")]
    plano = row[idx("plano")]

    if data_sim == "SIM":
        renovadas.append(f"• {username} ({email}) - {plano} - {total}")
        try:
            soma_total += float(total.replace("€", "").replace(",", "."))
        except:
            pass

    if dias:
        try:
            if int(dias) <= 0:
                expiradas.append(f"• {username} - {email} - {plano} - {dias} dias")
        except:
            pass

    if aviso:
        emails_enviados.append(f"• {username} - {email} - {aviso}")

# --- Texto Final ---
texto = f"""✅ <b>Relatório Semanal 4US</b>
Período: {inicio_semana.strftime('%d/%m/%Y')} a {hoje.strftime('%d/%m/%Y')}

<b>Linhas Renovadas:</b> {len(renovadas)}
""" + "\n".join(renovadas[:10]) + ("\n..." if len(renovadas) > 10 else "")

texto += f"""

<b>Linhas Expiradas:</b> {len(expiradas)}
""" + "\n".join(expiradas[:10]) + ("\n..." if len(expiradas) > 10 else "")

texto += f"""

<b>Total Acumulado:</b> {soma_total:.2f} €

<b>Emails Enviados:</b> {len(emails_enviados)}
""" + "\n".join(emails_enviados[:10]) + ("\n..." if len(emails_enviados) > 10 else "")

# --- Enviar ---
if __name__ == "__main__":
    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto="✅ Relatório Semanal 4US",
        corpo=texto,
        username="Relatório",
        motivo="Relatório Semanal"
    )
def enviar_relatorio():
    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto="✅ Relatório Semanal 4US (automático)",
        corpo=texto,
        username="Relatório",
        motivo="Relatório semanal automático"
    )
