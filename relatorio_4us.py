import os
import json
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from email_utils import enviar_email

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = "Registo Diário"
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

# --- Função para gerar relatório baseado em Registo Diário ---
def gerar_relatorio(periodo_nome: str, data_inicio: datetime, data_fim: datetime):
    result = sheet.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME
    ).execute()
    valores = result.get("values", [])
    if not valores:
        return "❌ Não foi possível obter dados da sheet."

    headers = valores[0]
    rows = valores[1:]
    idx = lambda nome: headers.index(nome)

    adesoes = []
    renovacoes = []
    expirados = []
    soma_total = 0.0

    for row in rows:
        row += [""] * (len(headers) - len(row))  # completar linhas curtas
        try:
            data_reg = datetime.strptime(row[idx("Data")], "%d/%m/%Y")
        except:
            continue

        if not (data_inicio.date() <= data_reg.date() <= data_fim.date()):
            continue

        tipo = row[idx("Tipo")].strip().lower()
        username = row[idx("Username")]
        email = row[idx("Email")]
        plano = row[idx("Plano")]
        total_str = row[idx("Total (€)")]
        origem = row[idx("Fonte")]

        linha_info = f"• {username} / {email} / {plano} [{origem}]"

        try:
            total = float(total_str.replace(",", "."))
        except:
            total = 0.0

        if tipo == "adesão":
            adesoes.append(linha_info)
            soma_total += total
        elif tipo == "renovação":
            renovacoes.append(linha_info)
            soma_total += total
        elif tipo == "expirado":
            expirados.append(f"• {username} / {email} [{origem}]")

    texto = f"RELATÓRIO {periodo_nome.upper()} – 4US\n\n"
    texto += f"Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}\n\n"
    texto += "➕ Adesões:\n" + ("\n".join(adesoes) if adesoes else "Nenhuma adesão") + f"\n\nTotal: {len(adesoes)}\n\n"
    texto += "🔄 Renovações:\n" + ("\n".join(renovacoes) if renovacoes else "Nenhuma renovação") + f"\n\nTotal: {len(renovacoes)}\n\n"
    texto += "🛑 Expirados:\n" + ("\n".join(expirados) if expirados else "Nenhum serviço expirado") + f"\n\nTotal: {len(expirados)}\n\n"
    texto += f"💰 Total acumulado: {soma_total:.2f} €\n"

    return texto

# --- Relatórios semanais e mensais ---
def enviar_relatorio():
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = hoje.replace(day=1)

    relatorio_semanal = gerar_relatorio("Semanal", inicio_semana, hoje)
    relatorio_mensal = gerar_relatorio("Mensal", inicio_mes, hoje)

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

# --- Execução manual (caso corras o ficheiro direto) ---
if __name__ == "__main__":
    enviar_relatorio()
