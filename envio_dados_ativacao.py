import asyncio
import os
import requests
import json
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from email_utils import enviar_email  # ✅ Importa a função centralizada

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_CLIENTES")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
BOT_TOKEN = os.getenv("API_TOKEN")


def idx(headers, col):
    return headers.index(col)


def enviar_telegram(chat_id, texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": texto,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"📨 Mensagem enviada para {chat_id}")
        else:
            print(f"❌ Erro Telegram ({response.status_code}): {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem Telegram: {e}")
        return False


async def monitor_ativacoes():
    print("🚀 Monitor de ativações iniciado (loop a cada 30 segundos)...")

    json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if json_credentials:
        creds_dict = json.loads(json_credentials)
        creds = Credentials.from_service_account_info(creds_dict)
    else:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

    sheet = build('sheets', 'v4', credentials=creds)

    while True:
        try:
            result = sheet.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
            valores = result.get('values', [])
            headers = valores[0]
            rows = valores[1:]

            for row_idx, row in enumerate(rows, start=2):
                if len(row) <= idx(headers, "renovada_no_painel_e_tabela_de_clientes"):
                    continue

                status = row[idx(headers, "renovada_no_painel_e_tabela_de_clientes")].strip().upper()
                if status != "SIM":
                    continue

                try:
                    chat_id = row[idx(headers, "telegram_id")]
                    if not chat_id.strip():
                        continue
                except:
                    continue

                username = row[idx(headers, "username")]
                password = row[idx(headers, "password")]
                email = row[idx(headers, "email")]
                ref_extra = row[idx(headers, "ref_extra")]
                plano = row[idx(headers, "plano_novo")]
                vpn = row[idx(headers, "vpn")]
                conta_vpn = row[idx(headers, "conta_vpn")]
                expira_em = row[idx(headers, "expira_em")]
                dias_para_terminar = row[idx(headers, "dias_para_terminar")]

                corpo = f"""Olá {username},

✅ O teu serviço foi ativado com sucesso!

📋 Aqui estão os teus dados:
• Username: {username}
• Password: {password}
• Email: {email}
• Referência extra: {ref_extra}
• Plano: {plano}
• VPN: {vpn}
• Conta VPN: {conta_vpn}
• Expira em: {expira_em}
• Dias restantes: {dias_para_terminar}

Obrigado por escolheres a 4US 🙌
"""

                enviar_email(
                    destinatario=email,
                    assunto="✅ Serviço Ativado – Dados de Acesso",
                    corpo=corpo,
                    username=username,
                    motivo="Ativação Manual (coluna P)"
                )

                telegram_msg = (
                    f"✅ <b>Serviço Ativado</b>\n\n"
                    f"<b>👤 Username:</b> {username}\n"
                    f"<b>🔐 Password:</b> {password}\n"
                    f"<b>📧 Email:</b> {email}\n"
                    f"<b>📎 Referência:</b> {ref_extra}\n"
                    f"<b>📦 Plano:</b> {plano}\n"
                    f"<b>🔒 VPN:</b> {vpn}\n"
                    f"<b>🔑 Conta VPN:</b> {conta_vpn}\n"
                    f"<b>📅 Expira em:</b> {expira_em}\n"
                    f"<b>📆 Dias restantes:</b> {dias_para_terminar}"
                )
                enviar_telegram(chat_id, telegram_msg)

                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!P{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Dados Enviados"]]}
                ).execute()

                print(f"✅ Linha {row_idx} atualizada com 'Dados Enviados'")
                await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ Erro geral: {e}")

        await asyncio.sleep(30)


# Para testes locais (opcional)
if __name__ == "__main__":
    enviar_email(
        destinatario="notificacoes.4us@gmail.com",
        assunto="🚀 Teste com histórico",
        corpo="Este é um email de teste enviado via email_utils com registo.",
        username="teste",
        motivo="Teste manual"
    )
