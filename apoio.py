from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import dp, user_data

# --- Função auxiliar para verificar login ---
def login_obrigatorio(handler):
    async def wrapper(callback_query):
        dados = user_data.get(callback_query.from_user.id)
        if not dados or not dados.get("username"):
            await callback_query.message.answer("⚠️ Faz login primeiro para ver os teus dados.")
            return
        return await handler(callback_query, dados)
    return wrapper

# --- Teclado com as opções de apoio técnico ---
def teclado_apoio():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Android", callback_data="apoio_android")],
        [InlineKeyboardButton(text="💻 Windows", callback_data="apoio_windows")],
        [InlineKeyboardButton(text="🍏 iPhone/Mac", callback_data="apoio_apple")],
        [InlineKeyboardButton(text="📺 Smart TV", callback_data="apoio_tv")],
        [InlineKeyboardButton(text="💬 Apoio via Chat", url="https://t.me/hhcihs")]
    ])

# --- Comando "apoio" pelo botão do bot ---
@dp.callback_query(lambda c: c.data == "apoio")
async def apoio_tecnico_callback(callback_query: types.CallbackQuery):
    dados = user_data.get(callback_query.from_user.id)
    if not dados or not dados.get("username"):
        await callback_query.message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
        return
    await callback_query.message.answer("🛠 Qual destes dispositivos usas?", reply_markup=teclado_apoio())

# --- Comando "apoio" por mensagem escrita ---
@dp.message(lambda msg: msg.text and "apoio" in msg.text.lower())
async def menu_apoio_handler(message: Message):
    dados = user_data.get(message.from_user.id)
    if not dados or not dados.get("username"):
        await message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
        return
    await message.answer("🛠 Qual destes dispositivos usas?", reply_markup=teclado_apoio())

# --- Android ---
@dp.callback_query(lambda c: c.data == "apoio_android")
async def apoio_android(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "📲 <b>Apps compatíveis com Android</b>:\n\n"
        "🔸 https://platinum-apk.com/PlatinumTeam-7.0-v1001-1006-vpn.apk\n"
        "🔑 A password de acesso é: <code>PLATINUM2030</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 V7 – Instalação com os meus dados", callback_data="instalar_v7")]
        ])
    )

    await callback_query.message.answer(
        "🔸 https://platinum-apk.com/PlatinumTeam-6.0-v801.apk\n"
        "🔑 A password de acesso é: <code>PLATINUM2030</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 V6 – Instalação com os meus dados", callback_data="instalar_v6")]
        ])
    )

    await callback_query.message.answer(
        "🔸 https://platinum-apk.com/PlatinumTeamV2.apk\n"
        "🔑 A password de acesso é: <code>PLATINUM2030</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📲 V2 – Instalação com os meus dados", callback_data="instalar_v2")]
        ])
    )
    
    await callback_query.message.answer(
    "🔸 https://platinum-apk.com/PurplePLATINUMTEAM.apk\n"
    "🔑 A password de acesso é: <code>PLATINUM2030</code>",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 Purple – Instalação com os meus dados", callback_data="instalar_purple")]
        ])
    )
    await callback_query.message.answer(
    "🔸 https://platinum-apk.com/PlatinumGuardianVPN(3.0).apk\n"
    "🔑 A password de acesso é: <code>PLATINUM2030</code>",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📲 VPN – Instalação com os meus dados", callback_data="instalar_vpn")]
        ])
    )

    await callback_query.message.answer(
        "🔸 https://platinum-apk.com/smarters4-0.apk\n"
        "🔸 https://platinum-apk.com/mytvonline+.apk\n"
        "🔑 A password de acesso é: <code>PLATINUM2030</code>"
    )

@dp.callback_query(lambda c: c.data == "apoio_apple")
async def apoio_apple(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "🍏 <b>App recomendada para iPhone/Mac</b>:\n"
        "🔸 MYTVOnline+ IPTV Player 4+\n"
        "🔗 https://apps.apple.com/us/app/mytvonline-iptv-player/id6714452886"
    )


@dp.callback_query(lambda c: c.data == "instalar_v7")
async def procedimento_v7(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
        return

    username = user.get("username", "SEU_USERNAME")
    password = user.get("password", "SUA_PASSWORD")
    email = user.get("email", "SEU_EMAIL")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
        caption="1️⃣ Instala a app 'Downloader' da Play Store"
    )
    await callback_query.message.answer(
        "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\n"
        "Vai a ‘Definições’ > ‘O meu Android’ > ‘Opções de Programador’\n"
        "Ativa ‘Aplicações de fontes desconhecidas’ para a app Downloader."
    )
    await callback_query.message.answer(
        "<b>3️⃣ Abre a app Downloader</b> e escreve:\n"
        "<code>https://platinum-apk.com</code>"
    )
    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1ZIjc6nPq9cAcTQvnEPc0mz5L_z_NH2hW",
        caption="4️⃣ Seleciona a app 'PLATINUM V7 XCIPTV'"
    )
    await callback_query.message.answer(
        "<b>5️⃣ Escreve a password:</b> <code>PLATINUM2030</code>\n"
        "6️⃣ Aguarda o download e segue os passos de instalação.\n"
        "7️⃣ Ao abrir, escolhe o painel <b>PLATINUM OLD</b>.\n"
        f"8️⃣ Preenche com os teus dados:\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔐 Password: <code>{password}</code>\n"
        "9️⃣ Clica em <b>ENTRAR</b>.\n"
        "🔟 Aguarda o carregamento das categorias.\n"
        "✅ <b>APROVEITA O MOMENTO COM O CONTEÚDO DIGITAL AGORA NA TUA MÃO!</b>"
    )

@dp.callback_query(lambda c: c.data == "instalar_v6")
async def procedimento_v6(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
        return

    username = user.get("username", "SEU_USERNAME")
    password = user.get("password", "SUA_PASSWORD")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
        caption="1️⃣ Instala a app 'Downloader' da Play Store"
    )
    await callback_query.message.answer(
        "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\n"
        "Vai a ‘Definições’ > ‘O meu Android’ > ‘Opções de Programador’\n"
        "Ativa ‘Aplicações de fontes desconhecidas’ para a app Downloader."
    )
    await callback_query.message.answer(
        "<b>3️⃣ Abre a app Downloader</b> e escreve:\n"
        "<code>https://platinum-apk.com</code>"
    )
    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1ivI08loZf6JqywY8DxVM5Zctt7mM9b-B",
        caption="4️⃣ Seleciona a app 'PLATINUM V6 XCIPTV'"
    )
    await callback_query.message.answer(
        "<b>5️⃣ Escreve a password:</b> <code>PLATINUM2030</code>\n"
        "6️⃣ Aguarda o download e segue os passos de instalação.\n"
        "7️⃣ Ao abrir, escolhe o painel <b>PLATINUM OLD</b>.\n"
        f"8️⃣ Preenche com os teus dados:\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔐 Password: <code>{password}</code>\n"
        "9️⃣ Clica em <b>ENTRAR</b>.\n"
        "🔟 Aguarda o carregamento das categorias.\n"
        "✅ <b>APROVEITA O MOMENTO COM O CONTEÚDO DIGITAL AGORA NA TUA MÃO!</b>"
    )

@dp.callback_query(lambda c: c.data == "instalar_v2")
async def procedimento_v2(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
        return

    username = user.get("username", "SEU_USERNAME")
    password = user.get("password", "SUA_PASSWORD")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
        caption="1️⃣ Instala a app 'Downloader' da Play Store"
    )
    await callback_query.message.answer(
        "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\n"
        "Vai a ‘Definições’ > ‘O meu Android’ > ‘Opções de Programador’\n"
        "Ativa ‘Aplicações de fontes desconhecidas’ para a app Downloader."
    )
    await callback_query.message.answer(
        "<b>3️⃣ Abre a app Downloader</b> e escreve:\n"
        "<code>https://platinum-apk.com</code>"
    )
    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1eTYXhfpzw74lQg22XTkXbV7OzB19MO1q",
        caption="4️⃣ Seleciona a app 'PLATINUM V2 XCIPTV'"
    )
    await callback_query.message.answer(
        "<b>5️⃣ Escreve a password:</b> <code>PLATINUM2030</code>\n"
        "6️⃣ Aguarda o download e segue os passos de instalação.\n"
        "7️⃣ Ao abrir, escolhe o painel <b>PLATINUM OLD</b>.\n"
        f"8️⃣ Preenche com os teus dados:\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔐 Password: <code>{password}</code>\n"
        "9️⃣ Clica em <b>SIGN IN</b>.\n"
        "🔟 Aguarda o carregamento das categorias.\n"
        "✅ <b>APROVEITA O MOMENTO COM O CONTEÚDO DIGITAL AGORA NA TUA MÃO!</b>"
    )

@dp.callback_query(lambda c: c.data == "instalar_purple")
async def procedimento_purple(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
        return

    username = user.get("username", "SEU_USERNAME")
    password = user.get("password", "SUA_PASSWORD")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
        caption="1️⃣ Instala a app 'Downloader' da Play Store"
    )
    await callback_query.message.answer(
        "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\n"
        "Vai a ‘Definições’ > ‘O meu Android’ > ‘Opções de Programador’\n"
        "Ativa ‘Aplicações de fontes desconhecidas’ para a app Downloader."
    )
    await callback_query.message.answer(
        "<b>3️⃣ Abre a app Downloader</b> e escreve:\n"
        "<code>https://platinum-apk.com</code>"
    )
    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1DcLU55kb3JNAc6czmtmnlx4oV0yir_qP",
        caption="4️⃣ Seleciona a app 'Purple PLATINUM TEAM'"
    )
    await callback_query.message.answer(
        "<b>5️⃣ Escreve a password:</b> <code>PLATINUM2030</code>"
    )
    await callback_query.message.answer(
        "<b>6️⃣ Ativa ‘Aplicações de fontes desconhecidas’</b> para a app Purple — mesmo que surja a informação que esta app pode ser prejudicial ao dispositivo."
    )
    await callback_query.message.answer(
        "7️⃣ Aguarda o download e segue os passos de instalação."
    )
    await callback_query.message.answer(
        "8️⃣ Ao abrir, escolhe se o dispositivo é <b>Móvel</b> ou <b>TV</b> para a app se adaptar ao teu equipamento."
    )
    await callback_query.message.answer(
        f"9️⃣ Log In – Preenche com os dados indicados abaixo:\n"
        f"👤 Username: <code>{username}</code>\n"
        f"🔐 Password: <code>{password}</code>"
    )
    await callback_query.message.answer(
        "🔟 Clica em <b>ENTRAR</b>.\n"
        "1️⃣1️⃣ Aguarda o carregamento das categorias.\n"
        "✅ <b>APROVEITA O CONTEÚDO COM A EXPERIÊNCIA EXCLUSIVA DA APP PURPLE!</b>"
    )

@dp.callback_query(lambda c: c.data == "instalar_vpn")
async def procedimento_vpn(callback_query: types.CallbackQuery):
    user = user_data.get(callback_query.from_user.id)
    if not user:
        await callback_query.message.answer("⚠️ Erro ao identificar os teus dados. Por favor, faz Log In primeiro.")
        return

    email = user.get("email", "SEU_EMAIL")
    password = user.get("password", "SUA_PASSWORD")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1EJYyvbDe-PPsJ8c_LmcR7kNOTIXbr2qi",
        caption="1️⃣ Instala a app 'Downloader' da Play Store"
    )
    await callback_query.message.answer(
        "<b>2️⃣ Permite instalações de fontes desconhecidas:</b>\n"
        "Vai a ‘Definições’ > ‘O meu Android’ > ‘Opções de Programador’\n"
        "Ativa ‘Aplicações de fontes desconhecidas’ para a app Downloader."
    )
    await callback_query.message.answer(
        "<b>3️⃣ Abre a app Downloader</b> e escreve:\n"
        "<code>https://platinum-apk.com</code>"
    )
    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1Yi2VruRKK2m_QlnBp9PRsERyQwvqKM0U",
        caption="4️⃣ Seleciona a app 'Platinum Guardian VPN'"
    )
    await callback_query.message.answer(
        "<b>5️⃣ Escreve a password:</b> <code>PLATINUM2030</code>"
    )
    await callback_query.message.answer(
        "6️⃣ Aguarda o download e segue os passos de instalação."
    )
    await callback_query.message.answer(
        f"7️⃣ Abre a app VPN e escreve os dados indicados abaixo.\n\n"
        f"📧 Email: <code>{email}</code>\n"
        f"🔐 Password: <code>{password}</code>"
    )
    await callback_query.message.answer(
        "✅ <b>Faça AUTO SELECT e a VPN está agora ativa! A tua navegação está protegida e otimizada para streaming.</b>"
    )

@dp.message(lambda msg: msg.text and "apoio" in msg.text.lower())
async def menu_apoio_handler(message: Message):
    dados = user_data.get(message.from_user.id)
    if not dados or not dados.get("username"):
        await message.answer("⚠️ Para aceder ao apoio técnico precisas de fazer Log In primeiro.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📱 Android", callback_data="apoio_android")],
        [InlineKeyboardButton(text="💻 Windows", callback_data="apoio_windows")],
        [InlineKeyboardButton(text="🍏 iPhone/Mac", callback_data="apoio_apple")],
        [InlineKeyboardButton(text="📺 Smart TV", callback_data="apoio_tv")],
        [InlineKeyboardButton(text="💬 Apoio via Chat", url="https://t.me/hhcihs")]
    ])
    await message.answer("🛠 Qual destes dispositivos usas?", reply_markup=kb)
