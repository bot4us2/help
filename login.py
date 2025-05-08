# login.py
from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from googleapiclient.http import MediaFileUpload
import os
import tempfile
from config import bot, user_data, sheet_service, drive_service, SPREADSHEET_ID, SHEET_CLIENTES, PASTA_COMPROVATIVOS_ID, mapa_colunas

def register_handlers_login(dp: Dispatcher):
    @dp.message(lambda msg: msg.text == "🔐 Log In")
    async def menu_login_handler(message: types.Message):
        user_data[message.from_user.id] = {}
        await message.answer("Indica o teu <b>username</b> ou <b>email</b>:")

    @dp.message(lambda msg: msg.text and not user_data.get(msg.from_user.id, {}).get("etapa"))
    async def tratar_login(message: types.Message):
        user_input = message.text.strip().lower()
        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        correspondencias = []
        for row in rows:
            dados = dict(zip(headers, row + [""] * (len(headers) - len(row))))
            username = dados.get("username", "").strip().lower()
            email = dados.get("email", "").strip().lower()

            if user_input == email:
                correspondencias.append(dados)
            elif user_input == username:
                correspondencias = [dados]
                break

        if not correspondencias:
            await message.answer("❌ Utilizador não encontrado.")
            return

        if len(correspondencias) == 1:
            dados = correspondencias[0]
            user_data[message.from_user.id] = dados
            user_data[message.from_user.id]["username"] = dados.get("username", "").strip()
            resposta = "\n".join([
                f"👤 Username: {dados.get('username')}",
                f"🔐 Password: {dados.get('password')}",
                f"📧 Email: {dados.get('email')}",
                f"📌 Referência extra: {dados.get('ref_extra')}",
                f"📦 Plano: {dados.get('plano')}",
                f"🔑 VPN: {dados.get('conta_vpn')}",
                f"🕓 Criada em: {dados.get('vpn_criada_em')}",
                f"📡 Estado da linha: {dados.get('estado_da_linha')}",
                f"📅 Expira em: {dados.get('expira_em')}",
                f"📆 Dias restantes: {dados.get('dias_para_terminar')}",
                "\n🔻 Escolhe uma opção:"
            ])
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🧾 Renovar", callback_data="renovar")],
                [InlineKeyboardButton(text="🛠 Apoio Técnico", callback_data="apoio")]
            ])
            await message.answer(resposta, reply_markup=kb)
            return

        # Mais do que uma correspondência (pelo email)
        user_data[message.from_user.id] = {"email_para_login": user_input}
        botoes = []
        for dados in correspondencias:
            username = dados.get("username", "")
            ref = dados.get("ref_extra", "") or "sem referência"
            texto = f"{username} — {ref}"
            botoes.append([InlineKeyboardButton(text=texto, callback_data=f"escolher_username:{username}")])

        await message.answer("📧 Foram encontrados vários acessos com este email. Escolhe qual desejas consultar:", 
                             reply_markup=InlineKeyboardMarkup(inline_keyboard=botoes))

    @dp.callback_query(lambda c: c.data.startswith("username_"))
    async def escolher_username(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        user = user_data.get(user_id)
        
        if not user:
            await callback_query.message.answer("⚠️ Sessão expirada ou inválida. Por favor, volta ao menu principal com /start.")
            return

        username = callback_query.data.split("_", 1)[1]
        user["username_escolhido"] = username

        email_original = user.get("email_para_login", "")
        ref_extra = user.get("ref_extra", "")
        plano = user.get("plano", "")
        conta_vpn = user.get("conta_vpn", "")
        estado = user.get("estado_da_linha", "")
        expira = user.get("expira_em", "")
        dias = user.get("dias_para_terminar", "")
        password = user.get("password", "")
        vpn_criada = user.get("vpn_criada_em", "")
        email = user.get("email", "")

        texto = (
            f"🧾 <b>Os teus dados</b>\n\n"
            f"👤 <b>Username:</b> {username}\n"
            f"🔑 <b>Password:</b> {password}\n"
            f"📧 <b>Email:</b> {email}\n"
            f"📌 <b>Referência Extra:</b> {ref_extra}\n"
            f"📦 <b>Plano:</b> {plano}\n"
            f"🌐 <b>VPN:</b> {conta_vpn} (criada em {vpn_criada})\n"
            f"📶 <b>Estado:</b> {estado}\n"
            f"📅 <b>Expira em:</b> {expira} ({dias} dias)"
        )

        botoes = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("🔄 Pretende Renovar", callback_data="renovar")],
            [InlineKeyboardButton("🛠 Apoio na instalação", callback_data="apoio_instalacao")],
            [InlineKeyboardButton("📩 Outros assuntos", callback_data="outros_assuntos")]
       ])

        await callback_query.message.answer(texto, reply_markup=botoes, parse_mode="HTML")

           
    @dp.callback_query(lambda c: c.data == "renovar")
    async def iniciar_renovacao(callback_query: types.CallbackQuery):
        user = user_data.get(callback_query.from_user.id)
        if not user:
            await callback_query.message.answer("⚠️ Não foi possível obter os teus dados. Faz login novamente.")
            return

        user["etapa"] = "renovacao_plano"

        planos = [
            ("Plano PT 6 Meses - 28.10€", "plano_pt_6_r"),
            ("Plano PT 12 Meses - 51.25€", "plano_pt_12_r"),
            ("Plano Full 6 Meses - 33.10€", "plano_full_6_r"),
            ("Plano Full 12 Meses - 61.25€", "plano_full_12_r")
        ]
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texto, callback_data=code)] for texto, code in planos
        ])
        await callback_query.message.answer("📦 Escolhe o novo plano:", reply_markup=kb)

    @dp.callback_query(lambda c: c.data.startswith("plano_") and c.data.endswith("_r"))
    async def escolher_vpn_renovacao(callback_query: types.CallbackQuery):
        planos = {
            "plano_pt_6_r": ("Plano PT 6 Meses", 28.10),
            "plano_pt_12_r": ("Plano PT 12 Meses", 51.25),
            "plano_full_6_r": ("Plano Full 6 Meses", 33.10),
            "plano_full_12_r": ("Plano Full 12 Meses", 61.25)
        }
        plano_nome, plano_valor = planos.get(callback_query.data, (None, None))

        if not plano_nome:
            await callback_query.message.answer("❌ Plano inválido. Tenta novamente.")
            return

        user = user_data[callback_query.from_user.id]
        user["plano_novo"] = plano_nome
        user["plano_valor"] = plano_valor

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="VPN 6M - 6€", callback_data="vpn6_r")],
            [InlineKeyboardButton(text="VPN 12M - 10€", callback_data="vpn12_r")],
            [InlineKeyboardButton(text="Sem VPN", callback_data="vpn0_r")]
        ])
        await callback_query.message.answer("🔒 Desejas adicionar VPN?", reply_markup=kb)

    @dp.callback_query(lambda c: c.data in ["vpn6_r", "vpn12_r", "vpn0_r"])
    async def mostrar_total_renovacao(callback_query: types.CallbackQuery):
        vpn_opcoes = {
            "vpn6_r": ("VPN 6 Meses", 6.0),
            "vpn12_r": ("VPN 12 Meses", 10.0),
            "vpn0_r": ("Sem VPN", 0.0)
        }
        vpn_nome, vpn_valor = vpn_opcoes[callback_query.data]
        user = user_data[callback_query.from_user.id]
        total = round((user["plano_valor"] + vpn_valor) * 1.025, 2)

        user["vpn"] = vpn_nome
        user["vpn_valor"] = vpn_valor
        user["total"] = f"{total:.2f}€"

        resumo = (
            f"📦 Plano escolhido: {user['plano_novo']}\n"
            f"🔒 VPN: {vpn_nome}\n"
            f"💰 Total com taxa: {user['total']}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📌 Confirmar e gerar referência", callback_data="confirmar_renovacao")]
        ])
        await callback_query.message.answer(resumo, reply_markup=kb)

    @dp.callback_query(lambda c: c.data == "confirmar_renovacao")
    async def gerar_referencia_renovacao(callback_query: types.CallbackQuery):
        user = user_data[callback_query.from_user.id]
        user["data/hora"] = datetime.now().strftime("%d-%m-%Y %H:%M")
        user["estado_do_pedido"] = "AGUARDA_COMPROVATIVO"
        user["conta_vpn"] = "4us/platinum"
        user["etapa"] = "comprovativo_renovacao"

        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        idx_username = headers.index("username")
        for i, row in enumerate(rows, start=2):
            if len(row) > idx_username and row[idx_username].strip().lower() == user["username"].strip().lower():
                for campo in [
                    "estado_do_pedido",
                    "comprovativo",
                    "renovada_no_painel_e_tabela_de_clientes",
                    "telegram_id"
                ]:
                    col = mapa_colunas.get(campo)
                    if col:
                        sheet_service.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID,
                            range=f"{SHEET_CLIENTES}!{col}{i}",
                            valueInputOption="RAW",
                            body={"values": [[""]]}
                        ).execute()

                for campo, chave in {
                    "vpn": "vpn",
                    "conta_vpn": "conta_vpn",
                    "plano_novo": "plano_novo",
                    "total": "total",
                    "data_hora": "data/hora",
                    "estado_do_pedido": "estado_do_pedido",
                    "telegram_id": str(callback_query.from_user.id)
                }.items():
                    col = mapa_colunas[campo]
                    valor = user.get(chave, chave)
                    sheet_service.spreadsheets().values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f"{SHEET_CLIENTES}!{col}{i}",
                        valueInputOption="RAW",
                        body={"values": [[valor]]}
                    ).execute()
                break

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📤 Carregar comprovativo", callback_data="comprovativo_renovacao")]
        ])
        await callback_query.message.answer(
            f"<b>📌 Dados para pagamento:</b>\n"
            f"🏦 Entidade: 20804\n"
            f"🔢 Referência: 903637523\n"
            f"💰 Valor: {user['total']}",
            reply_markup=kb
        )

    @dp.callback_query(lambda c: c.data == "comprovativo_renovacao")
    async def pedir_comprovativo_renovacao(callback_query: types.CallbackQuery):
        user_data[callback_query.from_user.id]["etapa"] = "comprovativo_renovacao"
        await callback_query.message.answer("📎 Envia agora o comprovativo (imagem ou PDF).")

    @dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("etapa") == "comprovativo_renovacao" and (msg.document or msg.photo))
    async def receber_comprovativo_renovacao(message: types.Message):
        user = user_data[message.from_user.id]
        nome_ref = user.get("username", "renovacao").replace(" ", "_")
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
        temp_path = os.path.join(tempfile.gettempdir(), nome_ficheiro)

        await bot.download_file(file.file_path, destination=temp_path)

        try:
            media = MediaFileUpload(temp_path, resumable=True)
            uploaded = drive_service.files().create(
                media_body=media,
                body={"name": nome_ficheiro, "parents": [PASTA_COMPROVATIVOS_ID]},
                fields="id"
            ).execute()
        except Exception as e:
            await message.answer("❌ Erro ao guardar o comprovativo. Tenta novamente.")
            print(f"❌ Erro ao subir ficheiro para o Drive: {e}")
            return

        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível apagar o ficheiro temporário: {e}")

        link = f"https://drive.google.com/file/d/{uploaded['id']}/view?usp=sharing"

        sheet = sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_CLIENTES
        ).execute()
        valores = sheet.get("values", [])
        headers = valores[0]
        rows = valores[1:]

        idx_username = headers.index("username")

        for i, row in enumerate(rows, start=2):
            if len(row) > idx_username and row[idx_username].strip().lower() == user["username"].strip().lower():
                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{mapa_colunas['estado_do_pedido']}{i}",
                    valueInputOption="RAW",
                    body={"values": [["PAGO"]]}
                ).execute()

                sheet_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{SHEET_CLIENTES}!{mapa_colunas['comprovativo']}{i}",
                    valueInputOption="RAW",
                    body={"values": [[link]]}
                ).execute()
                from notificacao_upload import enviar_notificacao
                await enviar_notificacao("Renovacao", user, link)
                break
                
        await message.answer(
            f"✅ Comprovativo recebido com sucesso!\n\n"
            f"A tua renovação será processada em breve.\n"
            f"Irás receber email com os dados atualizados."
        )

