from venv import logger

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8519563776:AAFxQP5iV5UAGamhIXnQybdYz2F_U8bhkRw"
HR_GROUP_ID = -5009067957

FORM_COUNTER = 0

(
    LANG, PHOTO, DOCS,
    JOB, NAME, BIRTH, ADDRESS, PHONE,
    FAMILY, EXPERIENCE, LAST_JOBS, SCHEDULE,
    EDUCATION, LANGUAGES, SALARY,
    CHRONIC, DISPENSARY, CRIMINAL, ARTICLE, EXTRA
) = range(20)

Q = {
    "ru": {
        "start": "Выберите язык:",
        "photo": "📸 Загрузите свою фотографию",
        "docs": "📎 Загрузите документы (PDF или Word)\nЕсли нет — нажмите «Пропустить»",
        "job": "💼 Желаемая должность",
        "name": "👤 ФИО",
        "birth": "📅 Дата рождения",
        "address": "🏠 Адрес проживания",
        "phone": "📞 Нажмите кнопку ниже, чтобы отправить номер телефона",
        "family": "👨‍👩‍👧 Семейное положение",
        "experience": "🛠 Опыт работы",
        "last_jobs": "🏢 Последние 3 места работы и причины увольнения",
        "schedule": "⏰ Предпочитаемый график работы",
        "education": "🎓 Образование",
        "languages": "🌍 Языки",
        "salary": "💰 Желаемая зарплата",
        "chronic": "🩺 Хронические заболевания",
        "dispensary": "🧠 Диспансерный учёт",
        "criminal": "⚖️ Судимость",
        "article": "📄 Если да — по какой статье?",
        "extra": "📝 Дополнительная информация (по желанию)\nМожно нажать «Пропустить»",
        "phone_error": "❗ Используйте кнопку для отправки номера телефона",
        "done": "✅ Анкета отправлена"
    },
    "uz": {
        "start": "Tilni tanlang:",
        "photo": "📸 Rasmingizni yuklang",
        "docs": "📎 Hujjatlaringizni yuklang (PDF yoki Word)\nAgar bo‘lmasa — «Пропустить»",
        "job": "💼 Qaysi lavozimda ishlamoqchisiz?",
        "name": "👤 Ism, familiya",
        "birth": "📅 Tug‘ilgan sana",
        "address": "🏠 Yashash manzili",
        "phone": "📞 Telefon raqamingizni tugma orqali yuboring",
        "family": "👨‍👩‍👧 Oilaviy holat",
        "experience": "🛠 Ish tajribasi",
        "last_jobs": "🏢 Oxirgi 3 ish joyi",
        "schedule": "⏰ Ish grafigi",
        "education": "🎓 Ma’lumoti",
        "languages": "🌍 Tillar",
        "salary": "💰 Kutilayotgan oylik",
        "chronic": "🩺 Surunkali kasalliklar",
        "dispensary": "🧠 Dispanser ro‘yxati",
        "criminal": "⚖️ Sudlanganmisiz?",
        "article": "📄 Qaysi modda bo‘yicha?",
        "extra": "📝 Qo‘shimcha ma’lumot (ixtiyoriy)\n«Пропустить» ni bosish mumkin",
        "phone_error": "❗ Telefon raqamni faqat tugma orqali yuboring",
        "done": "✅ Anketa yuborildi"
    }
}

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["🇷🇺 Русский", "🇺🇿 O‘zbekcha"]]
    await update.message.reply_text(
        Q["ru"]["start"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return LANG

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["lang"] = "ru" if "Рус" in update.message.text else "uz"
    await update.message.reply_text(
        Q[context.user_data["lang"]]["photo"],
        reply_markup=ReplyKeyboardRemove()
    )
    return PHOTO

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Фото"] = update.message.photo[-1].file_id
    kb = [["⏭ Пропустить"]]
    await update.message.reply_text(
        Q[context.user_data["lang"]]["docs"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return DOCS

async def docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["Документы"] = []
    if update.message.text == "⏭ Пропустить":
        await update.message.reply_text(Q[context.user_data["lang"]]["job"], reply_markup=ReplyKeyboardRemove())
        return JOB
    if update.message.document:
        context.user_data["Документы"].append(update.message.document.file_id)
        await update.message.reply_text(Q[context.user_data["lang"]]["job"], reply_markup=ReplyKeyboardRemove())
        return JOB
    await update.message.reply_text("📎 Загрузите документ или нажмите «Пропустить»")
    return DOCS

async def save(u, c, key, next_q, next_state):
    c.user_data[key] = u.message.text
    await u.message.reply_text(Q[c.user_data["lang"]][next_q])
    return next_state

async def job(u,c): return await save(u,c,"💼 Должность","name",NAME)
async def name(u,c): return await save(u,c,"👤 ФИО","birth",BIRTH)
async def birth(u,c): return await save(u,c,"📅 Дата рождения","address",ADDRESS)

async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["🏠 Адрес"] = update.message.text
    kb = [[KeyboardButton("📞 Отправить номер телефона", request_contact=True)]]
    await update.message.reply_text(
        Q[context.user_data["lang"]]["phone"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["📞 Телефон"] = update.message.contact.phone_number
        await update.message.reply_text(Q[context.user_data["lang"]]["family"], reply_markup=ReplyKeyboardRemove())
        return FAMILY
    await update.message.reply_text(Q[context.user_data["lang"]]["phone_error"])
    return PHONE

async def family(u,c): return await save(u,c,"👨‍👩‍👧 Семья","experience",EXPERIENCE)
async def exp(u,c): return await save(u,c,"🛠 Опыт","last_jobs",LAST_JOBS)
async def last(u,c): return await save(u,c,"🏢 Последние работы","schedule",SCHEDULE)
async def sched(u,c): return await save(u,c,"⏰ График","education",EDUCATION)
async def edu(u,c): return await save(u,c,"🎓 Образование","languages",LANGUAGES)
async def langq(u,c): return await save(u,c,"🌍 Языки","salary",SALARY)
async def salary(u,c): return await save(u,c,"💰 Зарплата","chronic",CHRONIC)
async def chronic(u,c): return await save(u,c,"🩺 Хронические","dispensary",DISPENSARY)
async def disp(u,c): return await save(u,c,"🧠 Диспансер","criminal",CRIMINAL)

async def criminal(update, context):
    context.user_data["⚖️ Судимость"] = update.message.text
    if update.message.text.lower() in ["да", "ha"]:
        await update.message.reply_text(Q[context.user_data["lang"]]["article"])
        return ARTICLE
    return await ask_extra(update, context)

async def article(update, context):
    context.user_data["📄 Статья"] = update.message.text
    return await ask_extra(update, context)

async def ask_extra(update, context):
    kb = [["⏭ Пропустить"]]
    await update.message.reply_text(
        Q[context.user_data["lang"]]["extra"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return EXTRA

async def extra(update, context):
    context.user_data["📝 Комментарий"] = (
        "—" if update.message.text == "⏭ Пропустить" else update.message.text
    )
    return await finish(update, context)

# async def finish(update, context):
#     global FORM_COUNTER
#     FORM_COUNTER += 1
#
#     text = f"📋 АНКЕТА №{FORM_COUNTER}\n\n"
#     for k,v in context.user_data.items():
#         if k not in ["lang", "Фото", "Документы"]:
#             text += f"{k}: {v}\n"
#
#     await context.bot.send_photo(
#         HR_GROUP_ID,
#         context.user_data["Фото"],
#         caption=text[:1024]
#     )
#
#     await update.message.reply_text(
#         Q[context.user_data["lang"]]["done"],
#         reply_markup=ReplyKeyboardRemove()
#     )
#     return ConversationHandler.END
async def finish(update, context):
    global FORM_COUNTER
    FORM_COUNTER += 1

    text = f"📋 АНКЕТА №{FORM_COUNTER}\n\n"
    for k, v in context.user_data.items():
        if k not in ["lang", "Фото", "Документы"]:
            text += f"{k}: {v}\n"

    try:
        # ТЕСТ: сначала обычное сообщение (так проще понять, есть ли доступ)
        await context.bot.send_message(chat_id=HR_GROUP_ID, text="✅ Получена новая анкета. Отправляю фото...")

        await context.bot.send_photo(
            chat_id=HR_GROUP_ID,
            photo=context.user_data["Фото"],
            caption=text[:1024]
        )

        # (необязательно) переслать документы
        for file_id in context.user_data.get("Документы", []):
            await context.bot.send_document(chat_id=HR_GROUP_ID, document=file_id)

    except Exception:
        logger.exception("Не удалось отправить анкету в HR_GROUP_ID")
        await update.message.reply_text(
            "❗ Анкета заполнена, но не удалось отправить её в HR-группу.\n"
            "Проверьте: правильный ID группы и права бота."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        Q[context.user_data["lang"]]["done"],
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG:[MessageHandler(filters.TEXT, set_lang)],
            PHOTO:[MessageHandler(filters.PHOTO, photo)],
            DOCS:[MessageHandler(filters.ALL, docs)],
            JOB:[MessageHandler(filters.TEXT, job)],
            NAME:[MessageHandler(filters.TEXT, name)],
            BIRTH:[MessageHandler(filters.TEXT, birth)],
            ADDRESS:[MessageHandler(filters.TEXT, address)],
            PHONE:[MessageHandler(filters.ALL, phone)],
            FAMILY:[MessageHandler(filters.TEXT, family)],
            EXPERIENCE:[MessageHandler(filters.TEXT, exp)],
            LAST_JOBS:[MessageHandler(filters.TEXT, last)],
            SCHEDULE:[MessageHandler(filters.TEXT, sched)],
            EDUCATION:[MessageHandler(filters.TEXT, edu)],
            LANGUAGES:[MessageHandler(filters.TEXT, langq)],
            SALARY:[MessageHandler(filters.TEXT, salary)],
            CHRONIC:[MessageHandler(filters.TEXT, chronic)],
            DISPENSARY:[MessageHandler(filters.TEXT, disp)],
            CRIMINAL:[MessageHandler(filters.TEXT, criminal)],
            ARTICLE:[MessageHandler(filters.TEXT, article)],
            EXTRA:[MessageHandler(filters.ALL, extra)],
        },
        fallbacks=[]
    )
    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
