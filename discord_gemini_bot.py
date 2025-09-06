import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import aiohttp
import json
import random
import datetime
import os
from typing import Optional

# Cấu hình bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# ==== CONFIG ====
DISCORD_TOKEN = "MTQxMzc4MjMxMDI2Mzg0OTAxMw.GzUbB2.KaBVXmLqPhvPW6J2mSkKeMGdD0G6KUQQFK9hPo"
GEMINI_KEY = "AIzaSyBAMcGOaB-Cl_XQY3yrUM3V5Y2NW-AusPU"

# Cấu hình Gemini
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Dictionary lưu trữ lịch sử chat của từng user
chat_history = {}

@bot.event
async def on_ready():
    print(f'🚀 {bot.user} đã sẵn sàng hoạt động!')
    print(f'📊 Bot đang hoạt động trên {len(bot.guilds)} server(s)')
    print(f'🌐 Web server running on port {os.environ.get("PORT", 8000)}')
    await bot.change_presence(activity=discord.Game(name="🤖 Hỗ trợ bởi Gemini 2.0 | /help"))

# ==================== ERROR HANDLING NÂNG CAO ====================
import logging
logging.basicConfig(level=logging.INFO)

async def safe_send(ctx_or_channel, *args, **kwargs):
    """Safe send với error handling"""
    try:
        return await ctx_or_channel.send(*args, **kwargs)
    except discord.Forbidden:
        print(f"❌ Không có quyền gửi tin nhắn tại {ctx_or_channel}")
    except discord.HTTPException as e:
        print(f"❌ Lỗi HTTP: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")

@bot.event
async def on_member_join(member):
    """Chào mừng thành viên mới"""
    channel = discord.utils.get(member.guild.channels, name='general')
    if channel:
        embed = discord.Embed(
            title="🎉 Chào mừng thành viên mới!",
            description=f"Xin chào {member.mention}! Chào mừng bạn đến với server **{member.guild.name}**",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Thành viên thứ", value=f"{member.guild.member_count}", inline=True)
        embed.add_field(name="Tham gia lúc", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        await channel.send(embed=embed)

# ==================== GEMINI AI COMMANDS ====================

@bot.command(name='gemini', aliases=['ai', 'chat'])
async def gemini_chat(ctx, *, question: str):
    """Chat với Gemini AI"""
    try:
        # Tạo embed loading
        embed = discord.Embed(
            title="🤖 Gemini AI đang suy nghĩ...",
            description="Vui lòng đợi trong giây lát",
            color=0xffa500
        )
        message = await ctx.send(embed=embed)
        
        # Gửi câu hỏi tới Gemini
        response = model.generate_content(question)
        
        # Tạo embed response
        embed = discord.Embed(
            title="🤖 Gemini AI",
            description=response.text[:2000] if len(response.text) > 2000 else response.text,
            color=0x4285f4
        )
        embed.set_footer(text=f"Được hỏi bởi {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        embed.timestamp = datetime.datetime.now()
        
        await message.edit(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Không thể kết nối với Gemini AI: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='gemini_image', aliases=['img_ai'])
async def gemini_image_analysis(ctx):
    """Phân tích hình ảnh với Gemini"""
    if not ctx.message.attachments:
        await ctx.send("❌ Vui lòng đính kèm một hình ảnh để phân tích!")
        return
    
    try:
        attachment = ctx.message.attachments[0]
        if not attachment.content_type.startswith('image/'):
            await ctx.send("❌ Vui lòng đính kèm một file hình ảnh!")
            return
        
        # Tải hình ảnh
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                image_data = await resp.read()
        
        embed = discord.Embed(
            title="🖼️ Đang phân tích hình ảnh...",
            color=0xffa500
        )
        message = await ctx.send(embed=embed)
        
        # Sử dụng Gemini Pro Vision (cần model khác)
        # Đây là placeholder - bạn cần cấu hình thêm cho vision model
        embed = discord.Embed(
            title="🖼️ Phân tích hình ảnh",
            description="Tính năng phân tích hình ảnh đang được phát triển. Vui lòng sử dụng lệnh /gemini để chat văn bản.",
            color=0x4285f4
        )
        await message.edit(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Không thể phân tích hình ảnh: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# ==================== UTILITY COMMANDS ====================

@bot.command(name='weather', aliases=['thoitiet'])
async def weather(ctx, *, city: str = "Hà Nội"):
    """Xem thời tiết (demo)"""
    # Đây là demo - bạn cần API key thời tiết thực
    embed = discord.Embed(
        title=f"🌤️ Thời tiết tại {city}",
        description="Tính năng thời tiết đang được phát triển",
        color=0x87ceeb
    )
    embed.add_field(name="Nhiệt độ", value="25°C", inline=True)
    embed.add_field(name="Độ ẩm", value="70%", inline=True)
    embed.add_field(name="Tình trạng", value="Có mây", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='translate', aliases=['dich'])
async def translate_text(ctx, target_lang: str, *, text: str):
    """Dịch văn bản với Gemini"""
    try:
        prompt = f"Translate the following text to {target_lang}: {text}"
        response = model.generate_content(prompt)
        
        embed = discord.Embed(
            title="🌐 Dịch thuật",
            color=0x00ff00
        )
        embed.add_field(name="Văn bản gốc", value=text[:500], inline=False)
        embed.add_field(name=f"Dịch sang {target_lang}", value=response.text[:500], inline=False)
        embed.set_footer(text=f"Được dịch bởi {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Lỗi khi dịch: {str(e)}")

# ==================== FUN COMMANDS ====================

@bot.command(name='joke', aliases=['truyen_cuoi'])
async def random_joke(ctx):
    """Kể chuyện cười"""
    try:
        prompt = "Kể một câu chuyện cười vui nhộn và tích cực bằng tiếng Việt"
        response = model.generate_content(prompt)
        
        embed = discord.Embed(
            title="😂 Chuyện cười",
            description=response.text,
            color=0xffff00
        )
        embed.set_footer(text="Được tạo bởi Gemini AI")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Không thể kể chuyện cười: {str(e)}")

@bot.command(name='quote', aliases=['cau_noi_hay'])
async def inspirational_quote(ctx):
    """Câu nói hay động viên"""
    try:
        prompt = "Chia sẻ một câu nói hay, tích cực và động viên bằng tiếng Việt"
        response = model.generate_content(prompt)
        
        embed = discord.Embed(
            title="✨ Câu nói hay",
            description=response.text,
            color=0xffd700
        )
        embed.set_footer(text="Cảm hứng từ Gemini AI")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Không thể lấy câu nói hay: {str(e)}")

@bot.command(name='dice', aliases=['xuc_xac'])
async def roll_dice(ctx, sides: int = 6):
    """Tung xúc xắc"""
    if sides < 2:
        await ctx.send("❌ Xúc xắc phải có ít nhất 2 mặt!")
        return
    
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="🎲 Tung xúc xắc",
        description=f"Kết quả: **{result}** (xúc xắc {sides} mặt)",
        color=0xff6347
    )
    await ctx.send(embed=embed)

# ==================== MODERATION COMMANDS ====================

@bot.command(name='clear', aliases=['xoa'])
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 5):
    """Xóa tin nhắn (cần quyền quản lý tin nhắn)"""
    if amount > 100:
        await ctx.send("❌ Không thể xóa quá 100 tin nhắn cùng lúc!")
        return
    
    deleted = await ctx.channel.purge(limit=amount + 1)
    embed = discord.Embed(
        title="🧹 Dọn dẹp hoàn tất",
        description=f"Đã xóa {len(deleted)-1} tin nhắn",
        color=0x00ff00
    )
    message = await ctx.send(embed=embed)
    await asyncio.sleep(3)
    await message.delete()

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member, *, reason: str = "Không có lý do"):
    """Kick thành viên (cần quyền kick)"""
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Đã kick thành viên",
            description=f"{member.mention} đã bị kick khỏi server",
            color=0xff4500
        )
        embed.add_field(name="Lý do", value=reason, inline=False)
        embed.add_field(name="Người thực hiện", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Không thể kick thành viên: {str(e)}")

# ==================== INFO COMMANDS ====================

@bot.command(name='serverinfo', aliases=['server'])
async def server_info(ctx):
    """Thông tin server"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 Thông tin server: {guild.name}",
        color=0x7289da
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Chủ server", value=guild.owner.mention, inline=True)
    embed.add_field(name="Số thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="Số kênh", value=len(guild.channels), inline=True)
    embed.add_field(name="Ngày tạo", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Vùng", value=str(guild.preferred_locale), inline=True)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
    await ctx.send(embed=embed)

@bot.command(name='userinfo', aliases=['user'])
async def user_info(ctx, member: discord.Member = None):
    """Thông tin người dùng"""
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"👤 Thông tin: {member.display_name}",
        color=member.color
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Trạng thái", value=str(member.status), inline=True)
    embed.add_field(name="Tham gia server", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
    embed.add_field(name="Tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
    embed.add_field(name="Vai trò cao nhất", value=member.top_role.mention, inline=True)
    await ctx.send(embed=embed)

@bot.command(name='help_custom', aliases=['huong_dan'])
async def help_command(ctx):
    """Hướng dẫn sử dụng bot"""
    embed = discord.Embed(
        title="🤖 Hướng dẫn sử dụng Bot",
        description="Danh sách các lệnh có sẵn:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🤖 AI Commands",
        value="`/gemini <câu hỏi>` - Chat với Gemini AI\n`/gemini_image` - Phân tích hình ảnh\n`/translate <ngôn ngữ> <văn bản>` - Dịch văn bản",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Fun Commands", 
        value="`/joke` - Chuyện cười\n`/quote` - Câu nói hay\n`/dice [số mặt]` - Tung xúc xắc",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Info Commands",
        value="`/serverinfo` - Thông tin server\n`/userinfo [@user]` - Thông tin người dùng\n`/weather [thành phố]` - Thời tiết",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Mod Commands",
        value="`/clear [số lượng]` - Xóa tin nhắn\n`/kick @user [lý do]` - Kick thành viên",
        inline=False
    )
    
    embed.set_footer(text="Sử dụng / trước mỗi lệnh")
    await ctx.send(embed=embed)

# ==================== ERROR HANDLING ====================

@bot.event
async def on_command_error(ctx, error):
    """Xử lý lỗi lệnh"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Lệnh không tồn tại",
            description="Sử dụng `/help_custom` để xem danh sách lệnh",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Thiếu tham số! Kiểm tra lại cú pháp lệnh.")
    else:
        await ctx.send(f"❌ Đã xảy ra lỗi: {str(error)}")

# ==================== AUTO RESPONSES ====================

@bot.event
async def on_message(message):
    """Auto response cho một số từ khóa"""
    if message.author == bot.user:
        return
    
    # Auto response
    content = message.content.lower()
    if 'xin chào' in content or 'hello' in content:
        await message.add_reaction('👋')
    elif 'cảm ơn' in content or 'thank' in content:
        await message.add_reaction('❤️')
    
    await bot.process_commands(message)

if __name__ == "__main__":
    # Chạy bot
    print("Đang khởi động Discord Bot...")
    print("Nhớ thay thế DISCORD_TOKEN và GEMINI_API_KEY bằng keys thật!")
    bot.run(DISCORD_TOKEN)