import asyncio  # certifica-te que está no topo
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import json
from email_utils import enviar_email

# Carrega variáveis de ambiente
load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_NAME = os.getenv("SHEET_CLIENTES")
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")

if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

async def verificar_notificacoes_renovacao():
    print("\n🚀 A iniciar aviso de renovação...\n")

    result = sheet.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    valores = result.get('values', [])
    headers = valores[0]
    rows = valores[1:]

    print(f"📊 Total de linhas na sheet: {len(rows)}\n")

    def idx(nome):
        return headers.index(nome)

    contadores = {
        "10": 0,
        "5": 0,
        "1": 0,
        "-7": 0,
        "falhas_envio": 0,
        "falhas_historico": 0
    }

    for row_idx, row in enumerate(rows, start=2):
        print(f"🔎 A processar linha {row_idx}...")
        row += [""] * (len(headers) - len(row))

        try:
            dias = int(row[idx("dias_para_terminar")].strip())
        except:
            continue

        aviso = row[idx("aviso_renovacao_enviado")].strip().lower()
        email_cliente = row[idx("email")]
        username = row[idx("username")]
        plano = row[idx("plano")]
        expira_em = row[idx("expira_em")]
        ref_extra = row[idx("ref_extra")]
        conta_vpn = row[idx("conta_vpn")]

        def enviar(texto, assunto, tipo_dia):
            try:
                if enviar_email("notificacoes.4us@gmail.com", assunto, texto, username=username, motivo=f"Aviso {tipo_dia} dias"):
                    msg = f"Email {tipo_dia} dias enviado"
                    sheet.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{SHEET_NAME}!{chr(65 + idx('aviso_renovacao_enviado'))}{row_idx}",
                        valueInputOption="RAW",
                        body={"values": [[msg]]}
                    ).execute()
                    contadores[str(tipo_dia)] += 1
                else:
                    contadores["falhas_envio"] += 1
            except Exception as e:
                print(f"⚠️ Erro ao registar aviso {tipo_dia} dias na linha {row_idx}: {e}")
                contadores["falhas_historico"] += 1

        if dias == 10 and "email 10" not in aviso:
            assunto = "A sua linha expira em 10 dias"
            corpo = gerar_corpo_mensagem(email_cliente, username, ref_extra, conta_vpn, plano, expira_em, 10)
            enviar(corpo, assunto, 10)

        elif dias == 5 and "email 5" not in aviso:
            assunto = "A sua linha expira em 5 dias"
            corpo = gerar_corpo_mensagem(email_cliente, username, ref_extra, conta_vpn, plano, expira_em, 5)
            enviar(corpo, assunto, 5)

        elif dias == 1 and "email 1" not in aviso:
            assunto = "A sua linha expira amanhã"
            corpo = gerar_corpo_mensagem(email_cliente, username, ref_extra, conta_vpn, plano, expira_em, 1)
            enviar(corpo, assunto, 1)

        elif dias == -7 and "email -7" not in aviso:
            assunto = "Serviço expirado há 7 dias"
            corpo = gerar_corpo_mensagem(email_cliente, username, ref_extra, conta_vpn, plano, expira_em, -7)
            enviar(corpo, assunto, -7)

        await asyncio.sleep(0.1)  # pausa leve entre linhas

    print("\n✅ Fim do aviso de renovação.\n")
    return {
        "Enviados (10 dias)": contadores["10"],
        "Enviados (5 dias)": contadores["5"],
        "Enviados (1 dia)": contadores["1"],
        "Enviados (-7 dias)": contadores["-7"],
        "Falhas de envio": contadores["falhas_envio"],
        "Falhas no histórico": contadores["falhas_historico"]
    }


def gerar_corpo_mensagem(email_cliente, username, ref_extra, conta_vpn, plano, expira_em, dias):
    prefixo = {
        10: "expira em 10 dias",
        5: "expira em 5 dias",
        1: "expira em 1 dia",
        -7: "expirou há 7 dias"
    }.get(dias, "tem alteração no serviço")

    corpo = f"""ENVIAR A: {email_cliente}
ASSUNTO: A sua linha {prefixo}

TEXTO:

Olá {ref_extra or username},

O seu serviço {prefixo} — no dia {expira_em}.

Resumo:
• Username: {username}
• Email: {email_cliente}
• Referência Extra: {ref_extra}
• Conta VPN: {conta_vpn}
• Plano: {plano}
• Expira em: {expira_em}

Para renovar:
1. Inicie o bot: https://t.me/fourus_help_bot
2. Clique em Log In
3. Introduza o seu username
4. Selecione Renovar
5. Escolha plano e VPN
6. Efetue o pagamento e envie o comprovativo

Com os melhores cumprimentos,  
A equipa 4US
"""
    return corpo
