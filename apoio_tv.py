# apoio_tv.py
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import dp, user_data

@dp.callback_query(lambda c: c.data == "apoio_tv")
async def apoio_tv(callback_query: types.CallbackQuery):
    dados = user_data.get(callback_query.from_user.id)
    if not dados or not dados.get("username"):
        await callback_query.message.answer("⚠️ Faz login primeiro para ver o apoio técnico.")
        return

    await callback_query.answer()  # desbloqueia o callback no Telegram

    await callback_query.message.answer(
        "📺 <b>Apoio para Smart TVs</b>\n\n"
        "Se a tua Smart TV tiver loja de apps:\n"
        "🔹 Procura <b>MyTVOnline+</b> ou <b>IPTV Smarters</b>\n"
        "🔹 Se não encontrares, podes instalar via navegador se a TV permitir.\n\n"
        "💡 A nossa sugestão na maioria das Smart TVs é a app IPTV SMARTERS pela sua fácil instalação.\n"
        "💬 Evita apps que usam MAC Address — causam instabilidade e extravio de linhas."
    )

    botoes = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📺 IPTV SMARTERS – Instalação com os meus dados", callback_data="smart_tv_smarters")],
        [InlineKeyboardButton(text="📺 MYTVOnline+ – Instalação (em breve)", callback_data="smart_tv_mytvonline")]
    ])

    await callback_query.message.answer("👇 Escolhe a app que pretendes usar:", reply_markup=botoes)

@dp.callback_query(lambda c: c.data == "smart_tv_smarters")
async def tutorial_smarters(callback_query: types.CallbackQuery):
    dados = user_data.get(callback_query.from_user.id)
    if not dados or not dados.get("username"):
        await callback_query.message.answer("⚠️ Faz login primeiro para ver os teus dados.")
        return

    username = dados.get("username", "SEU_USERNAME")
    password = dados.get("password", "SUA_PASSWORD")

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1LF5MJnRcfCsuYp_Iux3_wdzWbqcJfaz7",
        caption="📺 App IPTV SMARTERS – Instala na tua Smart TV se ainda não tens."
    )

    await callback_query.message.answer_photo(
        photo="https://drive.google.com/uc?export=view&id=1NQtF5fmm7vydo0FVHTqYxqas52Vs9Jjr",
        caption=(
            "⚙️ <b>Dados que vais precisar para a IPTV Smarters</b>\n\n"
            f"👤 Username: <code>{username}</code>\n"
            f"🔐 Password: <code>{password}</code>\n"
            "🌐 URL: <code>http://v6666.live:8080</code>"
        )
    )

    await callback_query.message.answer(
        "⚠️ <b>Antes de abrires qualquer canal:</b>\n"
        "Vai às <b>Definições</b> da app e garante que o <b>Stream Format = MPGTS</b>"
    )

    imagens_format = [
        ("1️⃣ Vai a 'Settings' e escolhe MPGTS", "1sw2ZIiddKg3ekbWi9yH6AGt1ojE8kfs_"),
        ("2️⃣ Confirma a seleção MPGTS", "1lifHlIC90ZXX3zyh2-qCzdDZy1PX89wE"),
        ("3️⃣ Exemplo com categoria carregada", "1rut_hZUXdjPuKGQGHSQOQn_A4Btx6T0q")
    ]

    for caption, img_id in imagens_format:
        await callback_query.message.answer_photo(
            photo=f"https://drive.google.com/uc?export=view&id={img_id}",
            caption=caption
        )

    await callback_query.message.answer("✅ Agora sim, disfruta da tua Smart TV com o melhor conteúdo 🎬🍿")
