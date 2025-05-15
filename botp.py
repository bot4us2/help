# botp.py
import asyncio
import logging
import apoio_tv
import apoio_windows
from aiogram import types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from config import bot, dp, user_data, sheet_service, drive_service, SPREADSHEET_ID, SHEET_CLIENTES, SHEET_PEDIDOS
from relatorio_4us import enviar_relatorio
from registo_diario import registar_eventos_diarios
from monitor_revendedores import monitor_resposta_revendedores


# --- MENU /start ---
@dp.message(lambda message: message.text == "/start")
async def menu_handler(message: types.Message):
    teclado_fixo = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 Log In"), KeyboardButton(text="➕ Adesão")],
        [KeyboardButton(text="👥 Rev")]  # Novo botão
    ],
    resize_keyboard=True
)
    await message.answer("Olá! Bem-vindo ao BOT 4US 🙌\nEscolhe uma opção abaixo:", reply_markup=teclado_fixo)

@dp.message(lambda message: True)
async def mostrar_chat_id(message: types.Message):
    if message.chat.type in ['group', 'supergroup']:
        await message.answer(
            f"✅ Este é o <b>chat_id</b> do grupo:\n<code>{message.chat.id}</code>",
            parse_mode="HTML"
        )
        print("DEBUG chat_id:", message.chat.id)


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
import adesao
import apoio
from envio_dados_ativacao import monitor_ativacoes
from notificacao_renovacao_estado_teste import verificar_notificacoes_renovacao

# --- LOOP DE NOTIFICAÇÕES ---
async def loop_notificacoes():
    while True:
        print("🔁 A correr verificação de notificações de renovação...\n")
        try:
            stats = await verificar_notificacoes_renovacao()
        except Exception as e:
            print(f"❌ Erro ao verificar notificações: {e}")
            stats = {}

        if stats:
            print("📊 RESUMO DA VERIFICAÇÃO DE RENOVAÇÕES:")
            for chave, valor in stats.items():
                print(f"• {chave}: {valor}")
            print("✅ Verificação concluída.\n")

        await asyncio.sleep(3600)  # a cada 60 minutos 3600

# --- LOOP DE RELATÓRIOS ---
#async def loop_relatorio():
#    while True:
#        print("🗓 A enviar relatório semanal...")
#       enviar_relatorio()
#        registar_eventos_diarios()
#        await asyncio.sleep(604800)  # 7 dias

# --- MAIN ---
import login
import carregamentos
async def main():
    try:
        logging.basicConfig(level=logging.INFO)
        await configurar_menu()
        login.register_handlers_login(dp)
        carregamentos.register_handlers_carregamentos(dp)

        print("✅ BOT 4US INICIADO")
        print("📡 A iniciar polling...")

        await asyncio.gather(
            dp.start_polling(bot),
            monitor_ativacoes(),
            loop_notificacoes(),
            monitor_resposta_revendedores()
        )

    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    import platform
    import sys

    try:
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Erro ao iniciar o bot: {e}")
        sys.exit(1)

