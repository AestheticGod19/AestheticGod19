import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
async def image(ctx):
    url = 'https://www.pexels.com/search/nature/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img', class_='photo-item__img')
    
    if images:
        image_urls = [img['src'] for img in images if img.get('src')]
        if image_urls:
            await ctx.send(random.choice(image_urls))
        else:
            await ctx.send('No images found.')
    else:
        await ctx.send('Could not scrape images.')

# --- START: fake web server for Render ---
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run)
t.start()
# --- END: fake web server ---

# Start the bot using your token
TOKEN = os.environ.get("DISCORD_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: DISCORD_TOKEN environment variable not set.")
