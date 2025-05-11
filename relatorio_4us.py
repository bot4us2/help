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

# --- Leitura da Sheet ---
result = sheet.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
valores = result.get("values", [])
headers = valores[0]
rows = valores[1:]

idx = lambda nome: headers.index(nome)

# --- Função para gerar relatório genérico (por período) ---
def gerar_relatorio(periodo_nome: str, data_inicio: datetime, data_fim: datetime):
    renovadas = []
    expiradas = []
    abandonadas = []
    soma_total = 0

    for row in rows:
        row += [""] * (len(headers) - len(row))

        try:
            dias = int(row[idx("dias_para_terminar")].strip())
        except:
            dias = None

        try:
            total = float(row[idx("total")].replace("€", "").replace(",", "."))
        except:
            total = 0.0

        username = row[idx("username")]
        email = row[idx("email")]
        plano = row[idx("plano")]
        estado = row[idx("estado_do_pedido")].strip().upper()
        data_hora = row[idx("data/hora")] if "data/hora" in headers else ""

        try:
            data_reg = datetime.strptime(data_hora, "%d-%m-%Y %H:%M") if data_hora else None
        except:
            data_reg = None

        if not data_reg or not (data_inicio <= data_reg <= data_fim):
            continue

        if dias == 0:
            expiradas.append(f"• {username} / {email}")

        if estado == "PAGO" and dias and dias > 10:
            renovadas.append(f"• {username} / {email}")
            soma_total += total

        if dias is not None and dias < -7:
            abandonadas.append(f"• {username} / {email}")

    texto = f"RELATÓRIO {periodo_nome.upper()} – 4US\n\nPeríodo: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\n"

    texto += "🛑 Expirados:\n" + ("\n".join(expiradas) if expiradas else "Nenhum serviço expirado") + f"\n\nTotal: {len(expiradas)}\n\n"
    texto += "🔄 Renovados:\n" + ("\n".join(renovadas) if renovadas else "Nenhuma renovação detectada") + f"\n\nTotal: {len(renovadas)}\n\n"
    texto += "❌ Abandonados:\n" + ("\n".join(abandonadas) if abandonadas else "Nenhum cliente passou dos -7 dias") + f"\n\nTotal: {len(abandonadas)}\n\n"
    texto += f"💰 Total acumulado: {soma_total:.2f} €\n"

    return texto

# --- Relatórios semanais e mensais ---
hoje = datetime.now()
inicio_semana = hoje - timedelta(days=hoje.weekday())
inicio_mes = hoje.replace(day=1)

relatorio_semanal = gerar_relatorio("Semanal", inicio_semana, hoje)
relatorio_mensal = gerar_relatorio("Mensal", inicio_mes, hoje)

if __name__ == "__main__":
    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Semanal – {hoje.strftime('%d/%m/%Y')}",
        corpo=relatorio_semanal,
        username="Relatório",
        motivo="Relatório Semanal"
    )

    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Mensal – {hoje.strftime('%d/%m/%Y')}",
        corpo=relatorio_mensal,
        username="Relatório",
        motivo="Relatório Mensal"
    )

def enviar_relatorio():
    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Semanal – {hoje.strftime('%d/%m/%Y')} (automático)",
        corpo=relatorio_semanal,
        username="Relatório",
        motivo="Relatório semanal automático"
    )
    enviar_email(
        destinatario=DESTINATARIO_RELATORIO,
        assunto=f"[4US] Relatório Mensal – {hoje.strftime('%d/%m/%Y')} (automático)",
        corpo=relatorio_mensal,
        username="Relatório",
        motivo="Relatório mensal automático"
    )
