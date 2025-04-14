import discord
from discord.ext import commands
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ⚠️ Replace these with your actual bot token and Tracker API key
TOKEN = os.getenv("DISCORD_TOKEN")
TRACKER_API_KEY = os.getenv("TRACKER_API_KEY")
LOL_PATCH_NOTES_URL = "https://www.leagueoflegends.com/en-us/news/tags/patch-notes/"
TFT_PATCH_NOTES_URL = "https://www.teamfighttactics.com/en-us/news/tags/patch-notes/"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Initialize patch variables
latest_patch = None  # The most recent patch
last_patch = None    # The previous patch

# Fetch the latest LoL patch information
async def fetch_latest_patch():
    global latest_patch, last_patch
    try:
        response = requests.get(LOL_PATCH_NOTES_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            first_article = soup.find("a", href=True)
            if first_article:
                patch_link = "https://www.leagueoflegends.com" + first_article["href"]
                patch_title = first_article.text.strip()

                # Fetch patch image from the patch page
                article_response = requests.get(patch_link)
                article_soup = BeautifulSoup(article_response.text, "html.parser")
                image = article_soup.find("meta", property="og:image")
                patch_image = image["content"] if image else None

                # If a new patch is detected, update last_patch before overwriting latest_patch
                if patch_title != latest_patch:
                    last_patch = latest_patch  # Store the previous patch
                    latest_patch = patch_title  # Update latest patch
                    
                    return patch_title, patch_link, patch_image, True  # True indicates a new patch was found
                return patch_title, patch_link, patch_image, False  # False means it's the same patch
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None, False

# Fetch the latest TFT patch information
async def fetch_latest_tft_patch():
    global latest_patch, last_patch
    try:
        response = requests.get(TFT_PATCH_NOTES_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            first_article = soup.find("a", href=True)
            if first_article:
                patch_link = "https://www.teamfighttactics.com" + first_article["href"]
                patch_title = first_article.text.strip()

                # Fetch patch image from the patch page
                article_response = requests.get(patch_link)
                article_soup = BeautifulSoup(article_response.text, "html.parser")
                image = article_soup.find("meta", property="og:image")
                patch_image = image["content"] if image else None

                # If a new patch is detected, update last_patch before overwriting latest_patch
                if patch_title != latest_patch:
                    last_patch = latest_patch  # Store the previous patch
                    latest_patch = patch_title  # Update latest patch
                    
                    return patch_title, patch_link, patch_image, True  # True indicates a new patch was found
                return patch_title, patch_link, patch_image, False  # False means it's the same patch
    except Exception as e:
        print(f"Error: {e}")
    return None, None, None, False

# Command to get LoL patch notes
@bot.command()
async def lolpatches(ctx):
    patch_title, patch_link, patch_image, is_new_patch = await fetch_latest_patch()
    if patch_title and patch_link:
        embed = discord.Embed(title=patch_title, url=patch_link, color=discord.Color.blue())
        if patch_image:
            embed.set_image(url=patch_image)
        await ctx.send(embed=embed if is_new_patch else "No new patch detected. You're up to date!")
    else:
        await ctx.send("No patches found.")

# Slash command to get LoL patch notes
@bot.tree.command(name="lolpatches", description="Get the latest League of Legends patch notes")
async def slash_lolpatches(interaction: discord.Interaction):
    await interaction.response.defer()  # Acknowledge the interaction

    patch_title, patch_link, patch_image, is_new_patch = await fetch_latest_patch()

    if patch_title and patch_link:
        embed = discord.Embed(title=patch_title, url=patch_link, color=discord.Color.blue())
        if patch_image:
            embed.set_image(url=patch_image)
        
        await interaction.followup.send(embed=embed)  # Use followup to send the message
    else:
        await interaction.followup.send("No patches found.")  # Use followup for error response


# Command to get TFT patch notes
@bot.command()
async def tftpatches(ctx):
    patch_title, patch_link, patch_image, is_new_patch = await fetch_latest_tft_patch()
    if patch_title and patch_link:
        embed = discord.Embed(title=patch_title, url=patch_link, color=discord.Color.green())  # Color for TFT
        if patch_image:
            embed.set_image(url=patch_image)
        await ctx.send(embed=embed if is_new_patch else "No new TFT patch detected. You're up to date!")
    else:
        await ctx.send("No TFT patches found.")

# Slash command to get TFT patch notes
@bot.tree.command(name="tftpatches", description="Get the latest TFT patch notes")
async def slash_tftpatches(interaction: discord.Interaction):
    patch_title, patch_link, patch_image, is_new_patch = await fetch_latest_tft_patch()
    if patch_title and patch_link:
        embed = discord.Embed(title=patch_title, url=patch_link, color=discord.Color.green())  # Color for TFT
        if patch_image:
            embed.set_image(url=patch_image)
        await interaction.response.send_message(embed=embed if is_new_patch else "No new TFT patch detected. You're up to date!")
    else:
        await interaction.response.send_message("No TFT patches found.")

# Command to get summoner stats (Tracker.gg API)
@bot.command()
async def lolstats(ctx, username: str, platform: str):
    """Fetch stats for a specific summoner."""
    url = f"https://api.tracker.gg/api/v2/lol/standard/profile/{platform}/{username}"
    headers = {"Authorization": f"Bearer {TRACKER_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers)
        
        # Check if the response is successful (status code 200)
        if response.status_code == 200:
            try:
                # Print the raw response content to debug
                print(f"Response Text: {response.text}")  # Debugging line
                
                data = response.json()

                # Check if the data contains the expected information
                if 'data' in data and 'segments' in data['data']:
                    segment = data['data']['segments'][0]
                    stats = segment.get('stats', {})
                    total_matches = stats.get('matchesPlayed', 'N/A')
                    total_wins = stats.get('wins', 'N/A')
                    total_losses = stats.get('losses', 'N/A')

                    summoner_name = data['data']['platformInfo']['platformId']
                    embed = discord.Embed(title=f"{summoner_name} Stats", color=discord.Color.green())
                    embed.add_field(name="Matches Played", value=str(total_matches), inline=False)
                    embed.add_field(name="Wins", value=str(total_wins), inline=False)
                    embed.add_field(name="Losses", value=str(total_losses), inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No summoner data found or the summoner's stats are unavailable.")
            except ValueError:
                await ctx.send("Error: Malformed response from the API.")
        else:
            # If the status code is not 200, print out the response text for more details
            await ctx.send(f"Error fetching stats: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error fetching stats: {str(e)}")

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Syncing commands globally (or guild-specific during testing)
    await bot.tree.sync()  # Sync commands globally (all guilds)
    
    print("Slash commands synced globally!")

bot.run(TOKEN)
