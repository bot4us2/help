# botp.py
import asyncio
import logging
from aiogram import types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from config import bot, dp, user_data, sheet_service, drive_service, SPREADSHEET_ID, SHEET_CLIENTES, SHEET_PEDIDOS

# --- MENU /start ---
@dp.message(lambda message: message.text == "/start")
async def menu_handler(message: types.Message):
    teclado_fixo = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔐 Log In"), KeyboardButton(text="➕ Adesão")]
        ],
        resize_keyboard=True
    )
    await message.answer("Olá! Bem-vindo ao BOT 4US 🙌\nEscolhe uma opção abaixo:", reply_markup=teclado_fixo)

# --- COMANDO /id PARA DETETAR CHAT_ID ---
@dp.message(lambda message: message.text == "/id")
async def enviar_chat_id(message: types.Message):
    await message.answer(f"O chat_id deste grupo é: <code>{message.chat.id}</code>", parse_mode="HTML")
    print(f"📣 chat_id detectado: {message.chat.id}")

# --- Comandos /menu ---
async def configurar_menu():
    await bot.set_my_commands([
        BotCommand(command="start", description="Iniciar o bot"),
        BotCommand(command="login", description="🔐 Log In"),
        BotCommand(command="adesao", description="➕ Adesão")
    ])

# --- IMPORTA OS MÓDULOS ---
import login
import adesao
import apoio
from envio_dados_ativacao import monitor_ativacoes
from notificacao_renovacao_estado_teste import verificar_notificacoes_renovacao

# --- MAIN ---
async def main():
    try:
        logging.basicConfig(level=logging.INFO)
        await configurar_menu()
        login.register_handlers_login(dp)
        print("✅ BOT 4US INICIADO")
        print("📡 A iniciar polling...")


        async def loop_notificacoes():
            while True:
                verificar_notificacoes_renovacao()
                await asyncio.sleep(43200)  # 12 horas

        await asyncio.gather(
            dp.start_polling(bot),
            monitor_ativacoes(),
            loop_notificacoes()
        )

    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"⚠️ Erro inesperado: {e}. A reiniciar em 5 segundos...")
            import time
            time.sleep(1)

