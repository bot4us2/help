from config import bot

NOTIFICACAO_CHAT_ID = -1002690078548
  # ID correto do grupo

async def enviar_notificacao(tipo, user, comprovativo_link):
    username = user.get("username", "sem username")
    email = user.get("email", "sem email")
    ref_extra = user.get("ref_extra", "sem ref")
    total = user.get("total") or f"{user.get('valor_total', '0')}€"
    data_hora = user.get("data/hora") or "data não definida"
    estado = user.get("estado_do_pedido", "estado desconhecido")
    telegram_id = user.get("telegram_id")
    link_telegram = f"tg://user?id={telegram_id}" if telegram_id else "#"

    nome = username if tipo == "Renovacao" else ref_extra

    texto = (
        f"<b>{tipo.upper()} SUBMETIDA</b>\n\n"
        f"<b>Nome / Referência:</b> {nome}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Username:</b> {username}\n"
        f"<b>Referência Extra:</b> {ref_extra}\n"
        f"<b>Total:</b> {total}\n"
        f"<b>Data/Hora:</b> {data_hora}\n"
        f"<b>Estado:</b> {estado}\n\n"
        f"<a href='{link_telegram}'>Abrir chat com cliente</a>\n"
        f"<a href='{comprovativo_link}'>Ver comprovativo</a>"
    )

    try:
        print(f"DEBUG - Enviando para chat_id: {NOTIFICACAO_CHAT_ID}")
        await bot.send_message(
            chat_id=NOTIFICACAO_CHAT_ID,
            text=texto,
            parse_mode="HTML",
            disable_web_page_preview=False
        )
    except Exception as e:
        print(f"❌ Erro ao enviar notificação para o grupo: {e}")
