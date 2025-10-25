import os
import requests
import telebot
from flask import Flask
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "🎤 Voice Bot is Running!"

API_KEY = "81ffa1604cd042c3a5e2e54338b7223e"
BOT_TOKEN = "8228742854:AAFBFCgyW8FfN5zYXdjuxE-sHaTtPi62W9w"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎤 أهلاً! أرسل لي رسالة صوتية وسأحولها لنص")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        msg = bot.reply_to(message, "⏳ جاري معالجة الصوت...")
        
        # تحميل الملف الصوتي
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = f"voice_{message.voice.file_id}.ogg"
        with open(file_name, 'wb') as f:
            f.write(downloaded_file)
        
        # رفع الملف لـ AssemblyAI
        headers = {'authorization': API_KEY}
        with open(file_name, 'rb') as f:
            upload_response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
        
        if upload_response.status_code == 200:
            upload_url = upload_response.json()['upload_url']
            
            transcript_request = {'audio_url': upload_url, 'language_code': 'ar'}
            transcript_response = requests.post('https://api.assemblyai.com/v2/transcript', 
                                              json=transcript_request, headers=headers)
            
            if transcript_response.status_code == 200:
                transcript_id = transcript_response.json()['id']
                
                # الانتظار للنتيجة
                for i in range(20):
                    status_response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
                    result = status_response.json()
                    
                    if result['status'] == 'completed':
                        text = result['text']
                        bot.edit_message_text(f"📝 النص:\n\n{text}", message.chat.id, msg.message_id)
                        os.remove(file_name)
                        return
                    elif result['status'] == 'error':
                        bot.edit_message_text("❌ خطأ في التحويل", message.chat.id, msg.message_id)
                        return
                    
                    time.sleep(5)
                
                bot.edit_message_text("⏰ انتهى الوقت المخصص", message.chat.id, msg.message_id)
        
        os.remove(file_name)
        
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

def run_bot():
    print("🤖 البوت شغال...")
    bot.polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=10000)
