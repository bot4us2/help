from config import bot
NOTIFICACAO_CHAT_ID = -4671183586  # <-- mete aqui o chat_id correto
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import smtplib
from email.mime.text import MIMEText
import time
import os
import json

SPREADSHEET_ID = '1X6PpQKvW5uFmuglzWC38yOfiwhFlOGMPu24F77sQwvM'
SHEET_NAME = 'Tabela de Clientes 2'
CREDENTIALS_FILE = 'credenciais_bot.json'

SMTP_USER = "notificacoes.4us@gmail.com"
SMTP_PASS = "hypdzcuivmypjmqw"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    CREDENTIALS_FILE = 'credenciais_bot.json'
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

result = sheet.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
valores = result.get('values', [])
headers = valores[0]
rows = valores[1:]

def idx(nome):
    return headers.index(nome)

def enviar_email(destinatario, assunto, corpo):
    try:
        msg_cliente = MIMEText(corpo, "plain")
        msg_cliente["Subject"] = assunto
        msg_cliente["From"] = SMTP_USER
        msg_cliente["To"] = destinatario

        msg_copia = MIMEText(corpo, "plain")
        msg_copia["Subject"] = f"[CÓPIA] {assunto}"
        msg_copia["From"] = SMTP_USER
        msg_copia["To"] = "notificacoes.4us@gmail.com"

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, destinatario, msg_cliente.as_string())
            server.sendmail(SMTP_USER, "notificacoes.4us@gmail.com", msg_copia.as_string())

        print(f"✅ Email enviado para {destinatario} + cópia")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

PLANOS_TEXTO = """

📋 Planos disponíveis:
• Plano PT 6 Meses – 27,50€
• Plano PT 12 Meses – 50,00€
• Plano Full 6 Meses – 32,50€
• Plano Full 12 Meses – 60,00€
• VPN 6 Meses – 6,00€
• VPN 12 Meses – 10,00€

A equipa 4US 🙌
"""

def verificar_notificacoes_renovacao():
    print("\n🚀 A iniciar aviso de renovação...\n")
    print(f"📊 Total de linhas na sheet: {len(rows)}\n")

    for row_idx, row in enumerate(rows, start=2):
        print(f"🔎 A processar linha {row_idx}...")
        row += [""] * (len(headers) - len(row))

        if len(row) <= idx("dias_para_terminar"):
            continue

        try:
            dias_str = row[idx("dias_para_terminar")].strip()
            dias = int(dias_str)
        except Exception as e:
            print(f"❌ Erro ao converter dias na linha {row_idx}: {e}")
            continue

        aviso = row[idx("aviso_renovacao_enviado")]
        email_cliente = row[idx("email")]
        username = row[idx("username")]
        plano = row[idx("plano")]
        expira_em = row[idx("expira_em")]
        ref_extra = row[idx("ref_extra")]
        conta_vpn = row[idx("conta_vpn")]

        if dias == -7 and ("email 1 dia enviado" in aviso.lower() or not aviso):
            assunto = "⚠️ AVISO: os teus dados serão removidos"
            corpo = f"""Olá {username},

O teu serviço expirou há 7 dias. Em breve os teus dados serão removidos do sistema.

📋 Os teus dados:
• Username: {username}
• Email: {email_cliente}
• Referência extra: {ref_extra}
• Conta VPN: {conta_vpn}
• Plano: {plano}
• Expirou em: {expira_em}

Se precisares de ajuda, responde a este email ou acede ao bot: https://t.me/fourus_help_bot

A equipa 4US 🙌
"""
            if enviar_email(email_cliente, assunto, corpo):
                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Eliminar linha e dados"]]}
                ).execute()

        elif dias == 1 and ("email 5 dia enviado" in aviso.lower() or not aviso):
            assunto = "⚠️ A tua linha expira amanhã!"
            corpo = f"""Olá {username},

O teu serviço expira em 1 dia — no dia {expira_em}.

📋 Os teus dados:
• Username: {username}
• Email: {email_cliente}
• Referência extra: {ref_extra}
• Conta VPN: {conta_vpn}
• Plano atual: {plano}
• Expira em: {expira_em}

Renova rapidamente através do nosso bot:
👉 https://t.me/fourus_help_bot

Ou responde a este email.
{PLANOS_TEXTO}
"""
            if enviar_email(email_cliente, assunto, corpo):
                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Email 1 dia enviado"]]}
                ).execute()

        elif dias == 5 and ("email 10 dia enviado" in aviso.lower() or not aviso):
            assunto = "⏳ A tua linha expira em 5 dias"
            corpo = f"""Olá {username},

O teu serviço expira em 5 dias — no dia {expira_em}.

📋 Os teus dados:
• Username: {username}
• Email: {email_cliente}
• Referência extra: {ref_extra}
• Conta VPN: {conta_vpn}
• Plano atual: {plano}
• Expira em: {expira_em}

Renova rapidamente através do nosso bot:
👉 https://t.me/fourus_help_bot

Ou responde a este email.
{PLANOS_TEXTO}
"""
            if enviar_email(email_cliente, assunto, corpo):
                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Email 5 dia enviado"]]}
                ).execute()

        elif dias == 10 and not aviso:
            assunto = "⏳ A tua linha expira em 10 dias"
            corpo = f"""Olá {username},

O teu serviço expira em 10 dias — no dia {expira_em}.

📋 Os teus dados:
• Username: {username}
• Email: {email_cliente}
• Referência extra: {ref_extra}
• Conta VPN: {conta_vpn}
• Plano atual: {plano}
• Expira em: {expira_em}

Renova rapidamente através do nosso bot:
👉 https://t.me/fourus_help_bot

Ou responde a este email.
{PLANOS_TEXTO}
"""
            if enviar_email(email_cliente, assunto, corpo):
                sheet.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                    valueInputOption="RAW",
                    body={"values": [["Email 10 dia enviado"]]}
                ).execute()

        elif dias > 10 and aviso.strip():
            print(f"🧹 A limpar aviso da linha {row_idx} (dias: {dias})")
            sheet.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                valueInputOption="RAW",
                body={"values": [[""]]}
            ).execute()

        # Pequena pausa opcional para evitar sobrecarga
        if row_idx % 20 == 0:
            time.sleep(1)

    print("\n✅ Fim do aviso de renovação.\n")
