import telebot
import yt_dlp
import os
import re

# Replace with your Telegram bot token
TOKEN = "7605886863:AAEHBZM9970vHnTn6KAbbsR0QAOfriLlxE4"
bot = telebot.TeleBot(TOKEN)

# Set download directory
DOWNLOAD_DIR = "D:/AIBOT/download"

# Ensure the download folder exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Function to sanitize filenames
def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)  # Removes special characters

# Function to download YouTube audio as MP3
def download_song(song_name):
    search_query = f"ytsearch:{song_name}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),  # Fix for Windows paths
        'noplaylist': True,
        'ffmpeg_location': r"D:\user\ffmpeg-2025-03-24-git-cbbc927a67-essentials_build\ffmpeg-2025-03-24-git-cbbc927a67-essentials_build\bin\ffmpeg.exe",
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '128',  # Reduce quality to reduce file size
        }],
        'quiet': False
    }    

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=True)
        
        if 'entries' in info:
            info = info['entries'][0]  # Get first search result

        original_filename = ydl.prepare_filename(info)  # This gives full path with original format
        print(f"🔹 Original filename: {original_filename}")  # Debugging output

        # Convert to .mp3 filename correctly
        base_name = os.path.splitext(os.path.basename(original_filename))[0]  # Extract name without extension
        sanitized_filename = sanitize_filename(base_name) + ".mp3"  # Add .mp3 extension
        final_path = os.path.join(DOWNLOAD_DIR, sanitized_filename)  # Corrected full path

        print(f"✅ Final filename (to be sent): {final_path}")  # Debugging output

        if os.path.exists(final_path):
            return final_path
        else:
            print(f"❌ Error: File not found - {final_path}")
            return None

# /start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Send me a song name, and I'll get it for you. 🎵")

# Handler for song requests
@bot.message_handler(func=lambda message: True)
def get_song(message):
    song_name = message.text
    bot.reply_to(message, f"🔍 Searching for '{song_name}'... 🎶")

    try:
        filename = download_song(song_name)
        print(f"📂 Downloaded file path: {filename}")  # Debugging output

        if filename and os.path.exists(filename):
            print("✅ File found! Sending to Telegram...")
            with open(filename, 'rb') as audio:
                bot.send_audio(message.chat.id, audio)
            print("✅ Song sent successfully!")
            os.remove(filename)  # Delete after sending
        else:
            bot.reply_to(message, "⚠️ Sorry, I couldn't find that song. Try another one!")
            print("❌ File not found after download.")

    except Exception as e:
        bot.reply_to(message, f"🚨 An error occurred: {e}")
        print(f"⚠️ Error: {e}")

print("🚀 Bot is running...")
bot.polling()
