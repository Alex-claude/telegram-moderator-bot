import logging
import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ModerationBot:
    def __init__(self):
        # Получаем токен из переменной окружения
        self.token = os.environ.get('BOT_TOKEN')
        
        # Список запрещенных слов (можете добавить свои)
        self.banned_words = [
            'спам', 'реклама', 'продам', 'куплю', 'заработок',
            'млм', 'пирамида', 'инвестиции', 'криптовалюта'
        ]
        
        # Список разрешенных доменов (если нужно)
        self.allowed_domains = ['youtube.com', 'youtu.be']
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await update.message.reply_text(
            "🤖 Бот-модератор активирован!\n\n"
            "Доступные команды:\n"
            "/start - запуск бота\n"
            "/rules - правила чата\n"
            "/stats - статистика модерации"
        )
    
    async def rules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /rules"""
        rules_text = (
            "📋 Правила чата:\n\n"
            "1️⃣ Запрещен спам и реклама\n"
            "2️⃣ Запрещены оскорбления\n" 
            "3️⃣ Ссылки только с разрешения админов\n"
            "4️⃣ Будьте вежливы и уважительны\n\n"
            "За нарушения - предупреждение или бан ⛔"
        )
        await update.message.reply_text(rules_text)
    
    async def moderate_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основная функция модерации"""
        message = update.message
        user = message.from_user
        text = message.text.lower() if message.text else ""
        
        # Проверка на запрещенные слова
        for word in self.banned_words:
            if word in text:
                try:
                    await message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"⚠️ @{user.username or user.first_name}, сообщение удалено: запрещенные слова"
                    )
                    logger.info(f"Удалено сообщение от {user.username}: содержит '{word}'")
                    return
                except Exception as e:
                    logger.error(f"Ошибка при удалении сообщения: {e}")
        
        # Проверка на ссылки
        if re.search(r'http[s]?://|www\.', text):
            # Проверяем, есть ли разрешенный домен
            allowed = False
            for domain in self.allowed_domains:
                if domain in text:
                    allowed = True
                    break
            
            if not allowed:
                try:
                    await message.delete()
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"🔗 @{user.username or user.first_name}, ссылки запрещены без разрешения админов"
                    )
                    logger.info(f"Удалена ссылка от {user.username}")
                    return
                except Exception as e:
                    logger.error(f"Ошибка при удалении ссылки: {e}")
        
        # Проверка на КАПС (много заглавных букв)
        if len(text) > 10 and text.isupper():
            try:
                await message.delete()
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"📢 @{user.username or user.first_name}, не нужно писать капсом"
                )
                logger.info(f"Удалено сообщение капсом от {user.username}")
                return
            except Exception as e:
                logger.error(f"Ошибка при удалении капса: {e}")
    
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика бота"""
        await update.message.reply_text(
            "📊 Статистика модерации:\n\n"
            "🤖 Бот работает исправно\n"
            "⚡ Проверяю все сообщения\n"
            "🛡️ Защищаю чат от спама\n\n"
            "Версия: 1.0"
        )
    
    def run(self):
        """Запуск бота"""
        if not self.token:
            logger.error("Токен бота не найден! Установите переменную BOT_TOKEN")
            return
        
        # Создаем приложение
        application = Application.builder().token(self.token).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("rules", self.rules))
        application.add_handler(CommandHandler("stats", self.stats))
        
        # Добавляем обработчик всех текстовых сообщений
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.moderate_message)
        )
        
        logger.info("Бот запущен!")
        
        # Запускаем бота
        application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    bot = ModerationBot()
    bot.run()
