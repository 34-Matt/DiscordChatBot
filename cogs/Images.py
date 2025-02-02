import io
import openai
import requests
from typing import Optional
import discord
from discord.ext import commands

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=['image', 'img', 'generation', 'generations', 'create'],
        help="Creates an image from the input text. Size of image can be specified by beginning the message with 256, 512, or 1024 (default 256).",
        brief="Generates an image."
        )
    async def Image(
        self, ctx,
        size: Optional[int] = commands.parameter(default=256, description="The size of the images (either 256, 512, or 1024)."),
        *,
        args: str = commands.parameter(default="NA", description="The prompt.")
    ):
        if size == 256:
            size_str = "256x256"
        elif size == 512:
            size_str = "512x512"
        elif size == 1024:
            size_str = "1024x1024"
        else:
            ctx.send(f'The size of {size} is not acceptable. Please try again with either 256, 512, or 1024.')
            return

        if args == "NA":
            ctx.send("Please enter a valid string prompt for creating an images.")
            return
        
        try:
            response = openai.Image.create(
                prompt = args,
                n = 1,
                size = size_str,
                user = ctx.author.name
            )
            image_url = response['data'][0]['url']
            img = requests.get(image_url).content
            with io.BytesIO(img) as file:
                await ctx.send("Created this image:", file=discord.File(file, 'yourImage.png'))
        except openai.error.OpenAIError as e:
            await ctx.send(f'An error occured with your request from OpenAI:\n{e.http_status}\n{e.error}')

async def setup(bot):
    await bot.add_cog(Images(bot))