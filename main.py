import discord
from discord.ext import commands
import os
import ollama
import json
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

MEMORY_FILE = "memory.json"


if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        conversation_history = json.load(f)
else:
    conversation_history = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, indent=2)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    user_input = message.content.strip()

    if user_input:
        try:

            if user_id not in conversation_history:
                conversation_history[user_id] = [
                    {"role": "system", "content": (
                        "You are a casual bot, neutral Discord bot. "
                        "Keep replies short, neutral, and boring. "
                        "Do NOT use emojis instead use text emoticons like :), :(, :D, and etc"
                    )}
                ]


            conversation_history[user_id].append({"role": "user", "content": user_input})


            response = ollama.chat(
                model="llama3",
                messages=conversation_history[user_id]
            )

            reply = response["message"]["content"]


            conversation_history[user_id].append({"role": "assistant", "content": reply})


            save_memory()

            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"⚠️ Error: {e}")

    await bot.process_commands(message)

bot.run(token)
