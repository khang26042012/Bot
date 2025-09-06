import discord
from discord import app_commands
from discord.ext import commands
import google.generativeai as genai

# ==== CONFIG ====
DISCORD_TOKEN = "MTQxMzc4MjMxMDI2Mzg0OTAxMw.GzUbB2.KaBVXmLqPhvPW6J2mSkKeMGdD0G6KUQQFK9hPo"
GEMINI_KEY = "AIzaSyBAMcGOaB-Cl_XQY3yrUM3V5Y2NW-AusPU"

# Cấu hình Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Cấu hình Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Khi bot online
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash commands đã sync: {len(synced)} lệnh")
    except Exception as e:
        print(f"❌ Sync lỗi: {e}")
    print(f"🤖 Bot AI đã đăng nhập: {bot.user}")


# Slash command /bot
@bot.tree.command(name="bot", description="Hỏi Gemini AI (chỉ bạn thấy câu trả lời)")
async def bot_chat(interaction: discord.Interaction, question: str):
    await interaction.response.defer(ephemeral=True, thinking=True)

    try:
        response = model.generate_content(question)
        answer = response.text

        if not answer:
            answer = "⚠️ Gemini không trả lời được."

        await interaction.followup.send(answer, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Lỗi: {e}", ephemeral=True)


# Run bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
