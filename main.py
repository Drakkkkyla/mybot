import asyncio
import discord
from discord.ext import commands
import os
import youtube_dl
import pafy
import random
import requests

# Создаем клиент Discord
intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# Список URL музыкальных треков
music_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=3JWTaaS7LdU",
    "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    # Добавьте здесь другие URL треков, которые вы хотите использовать
]

# Список шаблонов эквалайзера
equalizer_presets = {
    "flat": [0.0] * 14,
    "bass": [0.5, 0.5, 0.5, 0.5, 0.5, 0.6, 0.6, 0.7, 0.7, 0.8, 0.8, 0.9, 1.0, 1.0],
    "soft": [0.2, 0.2, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
    "high": [1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
}

# Команда длвя воспроизведения случайного музыкального трека
@client.command()
async def play_random(ctx):
    random_url = random.choice(music_urls)
    await play(ctx, random_url)

# Команда для воспроизведения музыки
@client.command()
async def play(ctx, url: str):
    if not ctx.author.voice:
        await ctx.send("Вы не находитесь в голосовом канале.")
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    await ctx.send("Пожалуйста, подождите 3 секунды перед тем как включить следующую песню.")
    await asyncio.sleep(3)

    download_audio(url)
    source = discord.FFmpegPCMAudio("video.mp3")
    ctx.voice_client.play(source)

# Команда для пропуска текущей песни
@client.command()
async def skip(ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    else:
        await ctx.send("Нет песни, которую можно пропустить.")

# Команда для отключения от голосового канала
@client.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу.")

# Команда для применения шаблона эквалайзера
@client.command()
async def eq(ctx, preset_name: str):
    if preset_name.lower() not in equalizer_presets:
        await ctx.send("Такого шаблона эквалайзера не существует.")
        return

    await ctx.send(f"Применен шаблон эквалайзера: {preset_name.lower()}")
    await ctx.send(f"```eq {', '.join(map(str, equalizer_presets[preset_name.lower()]))}```")

# Команда для отображения доступных шаблонов эквалайзера
@client.command()
async def eqpresets(ctx):
    presets_list = "\n".join(equalizer_presets.keys())
    await ctx.send(f"Доступные шаблоны эквалайзера:\n{presets_list}")

# Команда для выдачи списка команд
@client.command()
async def cm(ctx):
    embed = discord.Embed(title="Команды бота", description="Список доступных команд:", color=0x00ff00)
    embed.add_field(name="!play [url]", value="Начать проигрывание песни", inline=False)
    embed.add_field(name="!play_random", value="Начать проигрывание случайной песни", inline=False)
    embed.add_field(name="!skip", value="Пропустить текущую песню", inline=False)
    embed.add_field(name="!leave", value="Отключиться от голосового канала", inline=False)
    embed.add_field(name="!eq [preset]", value="Применить шаблон эквалайзера", inline=False)
    embed.add_field(name="!eqpresets", value="Показать доступные шаблоны эквалайзера", inline=False)
    await ctx.send(embed=embed)

# Команда для скачивания аудио с YouTube
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'video.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Обработка события подключения бота к серверу
@client.event
async def on_ready():
    print(f'Бот подключился к Discord и находится в сети под именем {client.user}')

# Обработка события присоединения нового участника
@client.event
async def on_member_join(member):
    print(f'{member} присоединился к серверу.')

# Обработка события отключения участника
@client.event
async def on_member_remove(member):
    print(f'{member} покинул сервер.')

# Запуск бота
client.run("BOT_TOKEN")
