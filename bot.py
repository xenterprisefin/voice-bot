import os
import telebot
from flask import Flask
from threading import Thread

app = Flask(__name__)

# حمل نموذج Whisper مرة واحدة
print("📥 جاري تحميل Whisper...")
os.system("pip install openai-whisper")
import whisper
model = whisper.load_model("base")
print("✅ تم تحميل النموذج!")

BOT_TOKEN = "8228742854:AAFBFCgyW8FfN5zYXdjuxE-sHaTtPi62W9w"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎤 البوت شغال! أرسل صوت وسأحوله لنص مجاناً")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        msg = bot.reply_to(message, "⏳ جاري التحويل...")
        
        # تحميل الملف
        file_info = bot.get_file(message.voice.file_id)
        file_path = f"voice_{message.message_id}.ogg"
        
        downloaded_file = bot.download_file(file_info.file_path)
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        # التحويل باستخدام Whisper
        result = model.transcribe(file_path, language="ar", fp16=False)
        text = result["text"]
        
        # تنظيف الملف
        os.remove(file_path)
        
        if text.strip():
            bot.edit_message_text(f"📝 النص:\n\n{text}", message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ لم يتعرف على نص", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {str(e)}")

print("🤖 البوت شغال بمحرك Whisper المجاني!")
Thread(target=lambda: bot.polling()).start()
app.run(host='0.0.0.0', port=8080)
