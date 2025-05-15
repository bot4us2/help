
# utils_carregamentos.py
from config import sheet_service, SPREADSHEET_ID
from datetime import datetime

def atualizar_registro_revendedor(username, valor, comprovativo_link, telegram_id):
    aba = "Revendedores"
    result = sheet_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=aba).execute()
    valores = result.get("values", [])
    headers = valores[0]
    rows = valores[1:]

    idx = lambda nome: headers.index(nome) if nome in headers else -1
    idx_nome = idx("Nome de utilizador")
    idx_telegram = idx("Telegram ID")
    idx_ult_valor = idx("Último carregamento")
    idx_link = idx("Último comprovativo")

    if idx_nome == -1:
        print("❌ Erro: coluna 'Nome de utilizador' não encontrada.")
        return

    datahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    for i, row in enumerate(rows, start=2):
        row += [""] * len(headers)
        if row[idx_nome].strip().lower() == username.strip().lower():
            # Atualizar colunas da aba Revendedores
            updates = {
                idx_telegram: telegram_id,
                idx_ult_valor: f"{valor}€ – {datahora}",
                idx_link: comprovativo_link
            }
            for idx_col, conteudo in updates.items():
                if idx_col >= 0:
                    col_letra = chr(65 + idx_col)
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{aba}!{col_letra}{i}",
                        valueInputOption="RAW",
                        body={"values": [[conteudo]]}
                    ).execute()
                else:
                    print(f"⚠️ Coluna não encontrada para update: {conteudo}")

            break

def registar_historico_carregamento(username, valor, comprovativo_link, telegram_id):
    aba = "Registo de Carregamentos"
    datahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    nova_linha = [[datahora, username, valor, comprovativo_link, str(telegram_id)]]

    sheet_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=aba,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": nova_linha}
    ).execute()
