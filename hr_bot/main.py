import os
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------- CONFIG ----------
# ВАЖНО: токен храните в переменных окружения, а не в коде.
# На сервере: export BOT_TOKEN="ВАШ_НОВЫЙ_ТОКЕН"
BOT_TOKEN = os.getenv("BOT_TOKEN", "8519563776:AAFxQP5iV5UAGamhIXnQybdYz2F_U8bhkRw").strip()

# Можно тоже вынести в env, но не обязательно
HR_GROUP_ID = int(os.getenv("HR_GROUP_ID", "-1003784655570"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан. Установите переменную окружения BOT_TOKEN.")

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
        "photo": "📸 Загрузите свою фотографию (можно как фото или файлом)",
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
        "criminal": "⚖️ Судимость (да/нет)",
        "article": "📄 Если да — по какой статье?",
        "extra": "📝 Дополнительная информация (по желанию)\nМожно нажать «Пропустить»",
        "phone_error": "❗ Используйте кнопку для отправки номера телефона",
        "done": "✅ Анкета отправлена",
        "send_photo_error": "❗ Не удалось отправить анкету в HR-группу. Проверьте ID группы и права бота.",
    },
    "uz": {
        "start": "Tilni tanlang:",
        "photo": "📸 Rasmingizni yuklang (foto yoki rasm fayl sifatida)",
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
        "criminal": "⚖️ Sudlanganmisiz? (ha/yo‘q)",
        "article": "📄 Qaysi modda bo‘yicha?",
        "extra": "📝 Qo‘shimcha ma’lumot (ixtiyoriy)\n«Пропустить» ni bosish mumkin",
        "phone_error": "❗ Telefon raqamni faqat tugma orqali yuboring",
        "done": "✅ Anketa yuborildi",
        "send_photo_error": "❗ HR guruhiga yuborib bo‘lmadi. Guruh ID va bot huquqlarini tekshiring.",
    }
}


# ---------- COMMON ----------
def _lang(context) -> str:
    return context.user_data.get("lang", "ru")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог отменён.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"chat_id = {update.effective_chat.id}")


# ---------- FLOW ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    kb = [["🇷🇺 Русский", "🇺🇿 O‘zbekcha"]]
    await update.message.reply_text(
        "Выберите язык / Tilni tanlang:",
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return LANG


async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "")
    context.user_data["lang"] = "ru" if "Рус" in txt else "uz"
    await update.message.reply_text(
        Q[_lang(context)]["photo"],
        reply_markup=ReplyKeyboardRemove()
    )
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Принимает фото в двух форматах:
    1) update.message.photo (обычное отправленное фото)
    2) update.message.document (если отправили картинку как файл)
    """
    file_id = None

    # Фото обычным способом
    if update.message.photo:
        file_id = update.message.photo[-1].file_id

    # Фото как файл (document), но это изображение
    elif update.message.document:
        mime = update.message.document.mime_type or ""
        if mime.startswith("image/"):
            file_id = update.message.document.file_id

    if not file_id:
        await update.message.reply_text("❗ Отправьте фотографию (как фото) или изображение файлом.")
        return PHOTO

    context.user_data["Фото"] = file_id

    kb = [["⏭ Пропустить"]]
    await update.message.reply_text(
        Q[_lang(context)]["docs"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return DOCS


async def docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    docs_list = context.user_data.setdefault("Документы", [])

    # Пропуск
    if update.message.text and update.message.text.strip() == "⏭ Пропустить":
        await update.message.reply_text(Q[_lang(context)]["job"], reply_markup=ReplyKeyboardRemove())
        return JOB

    # Документ
    if update.message.document:
        docs_list.append(update.message.document.file_id)
        await update.message.reply_text(Q[_lang(context)]["job"], reply_markup=ReplyKeyboardRemove())
        return JOB

    await update.message.reply_text("📎 Загрузите документ или нажмите «Пропустить»")
    return DOCS


async def save(u, c, key, next_q, next_state):
    c.user_data[key] = (u.message.text or "").strip()
    await u.message.reply_text(Q[_lang(c)][next_q])
    return next_state


async def job(u, c): return await save(u, c, "💼 Должность", "name", NAME)
async def name(u, c): return await save(u, c, "👤 ФИО", "birth", BIRTH)
async def birth(u, c): return await save(u, c, "📅 Дата рождения", "address", ADDRESS)


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["🏠 Адрес"] = (update.message.text or "").strip()
    kb = [[KeyboardButton("📞 Отправить номер телефона", request_contact=True)]]
    await update.message.reply_text(
        Q[_lang(context)]["phone"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["📞 Телефон"] = update.message.contact.phone_number
        await update.message.reply_text(Q[_lang(context)]["family"], reply_markup=ReplyKeyboardRemove())
        return FAMILY

    await update.message.reply_text(Q[_lang(context)]["phone_error"])
    return PHONE


async def family(u, c): return await save(u, c, "👨‍👩‍👧 Семья", "experience", EXPERIENCE)
async def exp(u, c): return await save(u, c, "🛠 Опыт", "last_jobs", LAST_JOBS)
async def last(u, c): return await save(u, c, "🏢 Последние работы", "schedule", SCHEDULE)
async def sched(u, c): return await save(u, c, "⏰ График", "education", EDUCATION)
async def edu(u, c): return await save(u, c, "🎓 Образование", "languages", LANGUAGES)
async def langq(u, c): return await save(u, c, "🌍 Языки", "salary", SALARY)
async def salary(u, c): return await save(u, c, "💰 Зарплата", "chronic", CHRONIC)
async def chronic(u, c): return await save(u, c, "🩺 Хронические", "dispensary", DISPENSARY)
async def disp(u, c): return await save(u, c, "🧠 Диспансер", "criminal", CRIMINAL)


async def criminal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ans = (update.message.text or "").strip()
    context.user_data["⚖️ Судимость"] = ans

    low = ans.lower()
    if low in ["да", "ha", "yes", "y"]:
        await update.message.reply_text(Q[_lang(context)]["article"])
        return ARTICLE

    return await ask_extra(update, context)


async def article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["📄 Статья"] = (update.message.text or "").strip()
    return await ask_extra(update, context)


async def ask_extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [["⏭ Пропустить"]]
    await update.message.reply_text(
        Q[_lang(context)]["extra"],
        reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True)
    )
    return EXTRA


async def extra(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text and update.message.text.strip() == "⏭ Пропустить":
        context.user_data["📝 Комментарий"] = "—"
        return await finish(update, context)

    if not update.message.text:
        await update.message.reply_text("Введите текст или нажмите «Пропустить».")
        return EXTRA

    context.user_data["📝 Комментарий"] = update.message.text.strip()
    return await finish(update, context)


async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global FORM_COUNTER
    FORM_COUNTER += 1

    text = f"📋 АНКЕТА №{FORM_COUNTER}\n\n"
    for k, v in context.user_data.items():
        if k not in ["lang", "Фото", "Документы"]:
            text += f"{k}: {v}\n"

    try:
        # Логируем ID группы и данные, которые пытаемся отправить
        logger.info(f"Attempting to send data to HR group with chat ID {HR_GROUP_ID}")
        logger.info(f"Attempting to send photo with ID {context.user_data['Фото']} and caption: {text[:1024]}")

        await context.bot.send_message(
            chat_id=HR_GROUP_ID,
            text="✅ Получена новая анкета. Отправляю фото..."
        )

        # Логируем успешную отправку сообщения
        logger.info("Sending photo to HR group...")
        await context.bot.send_photo(
            chat_id=HR_GROUP_ID,
            photo=context.user_data["Фото"],
            caption=text[:1024]
        )

        # Логируем отправку документов
        for file_id in context.user_data.get("Документы", []):
            logger.info(f"Sending document with file_id: {file_id}")
            await context.bot.send_document(chat_id=HR_GROUP_ID, document=file_id)

    except Exception as e:
        # Логируем исключение и ошибку отправки
        logger.exception(f"Failed to send the form to HR group. Error: {e}")
        await update.message.reply_text(Q[_lang(context)]["send_photo_error"], reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    await update.message.reply_text(
        Q[_lang(context)]["done"],
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("id", get_id))

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [MessageHandler(filters.TEXT, set_lang)],

            # ВАЖНО: принимает и PHOTO, и изображение-файл (document:image)
            PHOTO: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, photo)],

            DOCS: [MessageHandler(filters.ALL, docs)],
            JOB: [MessageHandler(filters.TEXT, job)],
            NAME: [MessageHandler(filters.TEXT, name)],
            BIRTH: [MessageHandler(filters.TEXT, birth)],
            ADDRESS: [MessageHandler(filters.TEXT, address)],
            PHONE: [MessageHandler(filters.ALL, phone)],
            FAMILY: [MessageHandler(filters.TEXT, family)],
            EXPERIENCE: [MessageHandler(filters.TEXT, exp)],
            LAST_JOBS: [MessageHandler(filters.TEXT, last)],
            SCHEDULE: [MessageHandler(filters.TEXT, sched)],
            EDUCATION: [MessageHandler(filters.TEXT, edu)],
            LANGUAGES: [MessageHandler(filters.TEXT, langq)],
            SALARY: [MessageHandler(filters.TEXT, salary)],
            CHRONIC: [MessageHandler(filters.TEXT, chronic)],
            DISPENSARY: [MessageHandler(filters.TEXT, disp)],
            CRIMINAL: [MessageHandler(filters.TEXT, criminal)],
            ARTICLE: [MessageHandler(filters.TEXT, article)],
            EXTRA: [MessageHandler(filters.ALL, extra)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()
