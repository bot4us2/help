# adesao.py
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import os
import tempfile
from contextlib import closing
from config import bot, dp, user_data, sheet_service, drive_service, SPREADSHEET_ID, SHEET_CLIENTES, PASTA_COMPROVATIVOS_ID, mapa_colunas
from email_utils import enviar_email
from notificacao_upload import enviar_notificacao

@dp.message(lambda msg: msg.text == "➕ Adesão")
async def menu_adesao_handler(message: types.Message):
    user_data[message.from_user.id] = {}
    user_data[message.from_user.id]["etapa"] = "nome"
    await message.answer("📝 Qual é o nome de quem vai usar a linha?")

@dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "nome")
async def etapa_nome(message: types.Message):
    user = user_data[message.from_user.id]
    user["ref_extra"] = message.text.strip()
    user["etapa"] = "email"
    await message.answer("📧 Agora indica o email:")

@dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "email")
async def etapa_email(message: types.Message):
    user = user_data[message.from_user.id]
    user["email"] = message.text.strip()
    user["etapa"] = None
    planos = [
        ("Plano PT 6 Meses - 28.10€", "plano_pt_6"),
        ("Plano PT 12 Meses - 51.25€", "plano_pt_12"),
        ("Plano Full 6 Meses - 33.10€", "plano_full_6"),
        ("Plano Full 12 Meses - 61.25€", "plano_full_12")
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=p[0], callback_data=p[1])] for p in planos])
    await message.answer("Escolhe o teu plano:", reply_markup=kb)

@dp.callback_query(lambda c: c.data in ["plano_pt_6", "plano_pt_12", "plano_full_6", "plano_full_12"])
async def escolher_vpn_adesao(callback_query: types.CallbackQuery):
    planos = {
        "plano_pt_6": ("Plano PT 6 Meses", 28.10),
        "plano_pt_12": ("Plano PT 12 Meses", 51.25),
        "plano_full_6": ("Plano Full 6 Meses", 33.10),
        "plano_full_12": ("Plano Full 12 Meses", 61.25)
    }
    plano_nome, plano_valor = planos[callback_query.data]
    user = user_data[callback_query.from_user.id]
    user["plano_escolhido"] = plano_nome
    user["plano_valor"] = plano_valor

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="VPN 6M - 6€", callback_data="vpn_6")],
        [InlineKeyboardButton(text="VPN 12M - 10€", callback_data="vpn_12")],
        [InlineKeyboardButton(text="Sem VPN", callback_data="vpn_0")]
    ])
    await callback_query.message.answer("Desejas adicionar VPN? (Android/Windows apenas)", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("vpn_"))
async def mostrar_total_adesao(callback_query: types.CallbackQuery):
    vpn_opcoes = {
        "vpn_6": ("VPN 6 Meses", 6.0),
        "vpn_12": ("VPN 12 Meses", 10.0),
        "vpn_0": ("Sem VPN", 0.0)
    }
    user = user_data[callback_query.from_user.id]
    vpn_nome, vpn_valor = vpn_opcoes[callback_query.data]
    total = round((user["plano_valor"] + vpn_valor) * 1.025, 2)

    user["vpn_escolhida"] = vpn_nome
    user["vpn_valor"] = vpn_valor
    user["valor_total"] = total

    resumo = (
        f"📦 Plano: {user['plano_escolhido']}\n"
        f"🔒 VPN: {vpn_nome}\n"
        f"💰 Total com taxa: {total:.2f}€"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Gerar Referência", callback_data="pagar_adesao")]
    ])
    await callback_query.message.answer(resumo, reply_markup=kb)

@dp.callback_query(lambda c: c.data == "pagar_adesao")
async def registar_adesao(callback_query: types.CallbackQuery):
    user = user_data[callback_query.from_user.id]
    agora = datetime.now().strftime("%d-%m-%Y %H:%M")

    nova_linha = [
        "SemNome", "semPass", user.get("email", ""), user.get("ref_extra", ""),
        "sem Plano", user.get("vpn_escolhida", ""), "4us/platinum", "atualizar",
        None, "", user.get("plano_escolhido", ""), f"{user.get('valor_total', '')}€",
        agora, "AGUARDA_COMPROVATIVO", "", "", str(callback_query.from_user.id)
    ]

    sheet_service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_CLIENTES,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [nova_linha]}
    ).execute()

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Carregar comprovativo", callback_data="comprovativo")]
    ])
    await callback_query.message.answer(
        f"<b>📌 Dados para pagamento:</b>\n🏦 Entidade: 20804\n🔢 Referência: 903637523\n💰 Valor: {user['valor_total']}€",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data == "comprovativo")
async def pedir_comprovativo(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_data[user_id]["etapa"] = "comprovativo"
    await callback_query.message.answer("📎 Envia agora o comprovativo (imagem ou PDF).")

@dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "comprovativo" and (msg.document or msg.photo))
async def receber_comprovativo(message: types.Message):
    user = user_data[message.from_user.id]
    ref_extra = user.get("ref_extra", "").strip().lower()
    nome_ref = ref_extra.replace(" ", "_") or "sem_nome"
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    if message.document:
        file_id = message.document.file_id
        nome_ficheiro = f"comprovativo_{nome_ref}_{agora}.{message.document.file_name.split('.')[-1]}"
    elif message.photo:
        file_id = message.photo[-1].file_id
        nome_ficheiro = f"comprovativo_{nome_ref}_{agora}.jpg"
    else:
        await message.answer("❌ Ficheiro inválido.")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    temp_path = os.path.join(tempfile.gettempdir(), nome_ficheiro)

    with closing(await bot.download_file(file_path)) as file_data:
        with open(temp_path, "wb") as f:
            f.write(file_data.read())

    try:
        media = MediaFileUpload(temp_path, resumable=True)
        uploaded = drive_service.files().create(
            media_body=media,
            body={"name": nome_ficheiro, "parents": [PASTA_COMPROVATIVOS_ID]},
            fields="id"
        ).execute()
    except Exception as e:
        print(f"❌ Erro ao subir para o Drive: {e}")
        await message.answer("⚠️ Erro ao guardar o comprovativo. Tenta novamente.")
        return

    link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"

    try:
        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        idx_ref = headers.index("ref_extra")
        idx_estado = headers.index("estado_do_pedido")
        idx_comprovativo = headers.index("comprovativo")

        for i, row in enumerate(rows, start=2):
            if len(row) > idx_ref and row[idx_ref].strip().lower() == ref_extra:
                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{chr(65+idx_estado)}{i}",
                    valueInputOption="RAW",
                    body={"values": [["PAGO"]]}
                ).execute()

                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{chr(65+idx_comprovativo)}{i}",
                    valueInputOption="RAW",
                    body={"values": [[link]]}
                ).execute()

                await enviar_notificacao("Nova Adesão", user, link)
                break
    except Exception as e:
        print(f"❌ Erro ao atualizar a Sheet: {e}")
        await message.answer("⚠️ Erro ao registar o comprovativo na Google Sheet.")
        return
    finally:
        os.remove(temp_path)

    await message.answer(
        f"✅ Comprovativo recebido com sucesso!\n\n"
        f"Obrigado! Seremos breves na ativação do teu serviço.\n"
        f"Assim que estiver ativo, vais receber email com os dados para:\n📧 <b>{user.get('email')}</b>"
    )

    # Envia email para equipa com dados resumidos da adesão
    corpo = f"""ENVIAR A: {user.get('email')}
ASSUNTO: Nova Adesão – Aguardando ativação

TEXTO:

Olá {user.get('ref_extra')},

Recebemos o seu comprovativo de pagamento.

Resumo da adesão:
• Email: {user.get('email')}
• Nome: {user.get('ref_extra')}
• Plano: {user.get('plano_escolhido')}
• VPN: {user.get('vpn_escolhida')}
• Total pago: {user.get('valor_total')}€

Assim que a linha for ativada, receberá os dados completos no seu email.

Se precisar de ajuda, utilize o nosso assistente:
https://t.me/fourus_help_bot

Com os melhores cumprimentos,
A equipa 4US
"""

    enviar_email(
        destinatario="notificacoes.4us@gmail.com",
        assunto="[BOT] Nova Adesão – Comprovativo Recebido",
        corpo=corpo,
        username=user.get("ref_extra", "adesao"),
        motivo="Adesão – comprovativo"
    )
