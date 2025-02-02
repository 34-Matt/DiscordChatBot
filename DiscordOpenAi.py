import os
import openai
import discord
from discord.ext import commands

from cogs import cogList

from dotenv import load_dotenv
load_dotenv()

token = os.getenv("DISCORD_TOKEN")
openai.api_key = os.getenv("OPENAI_TOKEN")
ollama_url = os.getenv("OLLAMA_URL")

intents= discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='!')
bot.ollama_url = ollama_url

@bot.event
async def on_ready():
    print('Adding cogs:')
    for cog in cogList:
        try:
            await bot.add_cog(cog(bot))
            print(f'Added {cog.__name__}')
        except commands.ExtensionAlreadyLoaded:
            print(f'{cog.__name__} is already loaded')
    print(f"Bot is now ready.")

bot.run(token)
