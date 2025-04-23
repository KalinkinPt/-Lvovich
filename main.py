import discord
import openai
import os
from datetime import datetime

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Счётчик GPT-4-запросов
gpt4_requests_today = 0
current_day = datetime.utcnow().day

@client.event
async def on_ready():
    print(f"✅ GPT-Бот запущений як {client.user}")

@client.event
async def on_message(message):
    global gpt4_requests_today, current_day

    if message.author == client.user:
        return

    # Сброс счётчика GPT-4 при переходе на следующий день
    if datetime.utcnow().day != current_day:
        current_day = datetime.utcnow().day
        gpt4_requests_today = 0

    if message.content.startswith("!Львович "):
        prompt = message.content[5:]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700
            )
            reply = response.choices[0].message.content
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"❌ Помилка: {e}")
        return

    if message.content.startswith("!Львович+ "):
        if gpt4_requests_today >= 20:
            await message.channel.send("⚠️ Ліміт на GPT-4 запити сьогодні вичерпано (20/день). Спробуйте завтра.")
            return

        prompt = message.content[7:]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ти професійний фізіотерапевт і викладач. Відповідай чітко, але розгорнуто, з прикладами, якщо доречно."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )
            reply = response.choices[0].message.content
            gpt4_requests_today += 1
            await message.channel.send(f"🧠 Львович каже:\n{reply}")

        except Exception as e:
            await message.channel.send(f"❌ Помилка GPT-4: {e}")
        return

client.run(DISCORD_TOKEN)
