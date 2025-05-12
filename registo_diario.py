import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SHEET_ORIGEM = "Tabela de Clientes 2"
SHEET_REGISTO = "Registo Diário"
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")

json_credentials = os.getenv("GOOGLE_CREDENTIALS_JSON")
if json_credentials:
    creds_dict = json.loads(json_credentials)
    creds = Credentials.from_service_account_info(creds_dict)
else:
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE)

sheet = build('sheets', 'v4', credentials=creds)

def idx(headers, nome):
    return headers.index(nome)

def registar_eventos_diarios():
    print("📥 A registar eventos diários...")

    hoje = datetime.now().strftime("%d/%m/%Y")
    hoje_dt = datetime.now().date()

    # --- Lê a aba de registo diário
    registo_existente = sheet.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_REGISTO
    ).execute().get("values", [])

    entradas_existentes = set()
    for linha in registo_existente[1:]:  # ignora cabeçalhos
        if len(linha) >= 3:
            entradas_existentes.add((linha[0], linha[2]))  # (data, username)

    # --- Lê a origem: Tabela de Clientes 2
    valores = sheet.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_ORIGEM
    ).execute().get("values", [])

    headers = valores[0]
    rows = valores[1:]
    novas_linhas = []

    for row in rows:
        row += [""] * (len(headers) - len(row))  # evitar IndexError
        try:
            username = row[idx(headers, "username")]
            email = row[idx(headers, "email")]
            plano = row[idx(headers, "plano_novo")] or row[idx(headers, "plano")]
            total = row[idx(headers, "total")].replace("€", "").strip()
            estado = row[idx(headers, "estado_do_pedido")].strip().upper()
            dias = int(row[idx(headers, "dias_para_terminar")])
            data_hora_str = row[idx(headers, "data/hora")].strip()
            fonte = "verificação (auto)"
        except Exception as e:
            continue

        # Verifica se a data do evento é de hoje
        try:
            data_dt = datetime.strptime(data_hora_str, "%d-%m-%Y %H:%M").date()
        except:
            continue

        if data_dt != hoje_dt:
            continue

        # Evita duplicações
        if (hoje, username) in entradas_existentes:
            continue

        # --- Tipos de evento ---
        if estado == "PAGO":
            tipo = "Adesão" if row[idx(headers, "plano_novo")] else "Renovação"
        elif dias in [0, -7]:
            tipo = "Expirado"
            total = ""
            plano = ""
        else:
            continue

        novas_linhas.append([
            hoje, tipo, username, email, plano, total, fonte, f"linha origem: {rows.index(row)+2}"
        ])

    if novas_linhas:
        sheet.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_REGISTO}!A1",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": novas_linhas}
        ).execute()
        print(f"✅ {len(novas_linhas)} novas entradas adicionadas ao registo diário.")
    else:
        print("ℹ️ Nenhuma entrada nova para registar.")
