import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# -----------------------------
# Web server for uptime monitor
# -----------------------------
app = Flask(__name__)

@app.get("/")
def home():
    return "OK", 200

def run_web():
    port = int(os.environ.get("PORT", "10000"))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# -----------------------------
# Discord bot (official)
# -----------------------------
TOKEN = os.getenv("TOKEN")  # BOT token
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID", "0"))

MUTE = os.getenv("MUTE", "false").lower() == "true"
DEAF = os.getenv("DEAF", "false").lower() == "true"

if not TOKEN:
    raise RuntimeError("Missing TOKEN env var (use BOT token).")

if not GUILD_ID or not VOICE_CHANNEL_ID:
    raise RuntimeError("Missing GUILD_ID or VOICE_CHANNEL_ID env vars.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("❌ Bot is not in that guild. Invite it first.")
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel:
        print("❌ Voice channel not found. Check VOICE_CHANNEL_ID.")
        return

    if not isinstance(channel, discord.VoiceChannel):
        print("❌ That channel ID is not a voice channel.")
        return

    # Connect / move
    if bot.voice_clients:
        vc = bot.voice_clients[0]
        await vc.move_to(channel)
    else:
        vc = await channel.connect()

    await vc.guild.change_voice_state(channel=channel, self_mute=MUTE, self_deaf=DEAF)
    print(f"✅ Joined voice: {channel.name} | mute={MUTE} deaf={DEAF}")

# Start web server, then bot
keep_alive()
bot.run(TOKEN)
