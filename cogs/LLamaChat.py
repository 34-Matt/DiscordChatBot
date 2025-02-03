from ollama import ResponseError, AsyncClient
from typing import Optional
from discord.ext import commands, tasks
import discord.ui as dui
from collections import UserList

import datetime


DELTATIME = datetime.timedelta(hours=1, minutes=0, seconds=0)


class ChatThread(UserList):
    def __init__(self, system, temperature, channel_string, timeout):
        super().__init__([{"role": "system", "content": system}])
        self.temperature = temperature
        self.channel_string = channel_string
        self.timeout = timeout
        
    def _create_msg(self, id, msg):
        self.timeout =datetime.datetime.now() + DELTATIME
        if id == 'system':
            item = {"role": "system", "content": msg}
        elif id == 'assistant':
            item = {"role": "assistant", "content": msg}
        else:
            item = {"role": "user", "content": msg}
        return item
        
    def __setitem__(self, index, id, msg):
        item = self._create_msg(id, msg)
        self.data.__setitem__(index, item)
        
    def insert(self, index, id, msg):
        item = self._create_msg(id, msg)
        self.data.insert(index, item)
        
    def append(self, id, msg):
        item = self._create_msg(id, msg)
        self.data.append(item)
        
    def pop(self):
        return self.data.pop()
        
    def extend(self, *args):
        raise NotImplementedError("Extending does not make much sense for this class")
        
    def getTemperature(self):
        return self.temperature


class DeepChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_thread = {}
        self.delete_thread.start()
        
        self.client = AsyncClient(
            host=bot.ollama_url
        )
            
            
    @tasks.loop(minutes=1)
    async def delete_thread(self):
        currentTime = datetime.datetime.now()
        delNames = []
        for name, thread in self.active_thread.items():
            if thread.timeout < currentTime:
                delNames.append(name)
                
                splitName = name.split(',')
                guild, channel = int(splitName[0]), int(splitName[1])
                guild = self.bot.get_guild(guild)
                channel = guild.get_channel(channel)
                
                await channel.send('Thread has timed out. Thanks for the conversation.')
        for name in delNames:
            del self.active_thread[name]


    @commands.command(
        aliases=['start', 'begin', 'listen'],
        help="Begin a conversation with ChatGPT. Can specify the temperature for creating a response by placing float at the start (default to 0.6). Can specify in text how you want ChatGPT to sound.",
        brief="Begin a conversation with ChatGPT."
        )
    async def Deepseek(
        self, ctx,
        temp:Optional[float] = commands.parameter(default = 0.6, description="The temperature for the conversation."),
        *,
        args=commands.parameter(default='NA', description="The initial system for the conversation.")
    ):
        if args == 'NA':
            args = "You are a helpful assistant."
            
        current_channel = str(ctx.guild.id) + ',' + str(ctx.channel.id)
        for ch in self.active_thread.keys():
            if ch == current_channel:
                await ctx.send('This thread is already active.')
        
        self.active_thread[current_channel] = ChatThread(args, temp, current_channel, datetime.datetime.now() + DELTATIME)
        print(self.active_thread[current_channel])
        await ctx.send('Hello, I am ready for our conversation.')

        #tokenCount, _ = util.extractTokenInfo(args, tiktoken.encoding_for_model("text-davinci-003"))


    @commands.Cog.listener('on_message')
    async def on_message(self, ctx):
        if ctx.author == self.bot.user:
            return
        
        current_channel = str(ctx.guild.id) + ',' + str(ctx.channel.id)
        if current_channel not in self.active_thread.keys():
            return
        
        if ctx.content[0] == self.bot.command_prefix:
            return

        self.active_thread[current_channel].append(ctx.id, ctx.content)

        try:
            print(self.active_thread[current_channel].data,)
            
            response = ''
            original_message = None
            async for part in await self.client.chat(
                model="deepseek-r1:1.5b",
                messages=self.active_thread[current_channel].data,
                stream=True,
                #temperature = self.active_thread[current_channel].getTemperature(),
                #user = ctx.author.name
            ):
                response += part.message.content
                text_main, text_thought = edit_responce(response)
                
                if not text_thought:
                    continue
                elif original_message is None:
                    original_message = await ctx.channel.send(text_main, view=DeepMessage(text_thought))
                else:
                    await original_message.edit(content=text_main, view=DeepMessage(text_thought))

            self.active_thread[current_channel].append('assistant', response)
            
        except ResponseError as e:
            print(e.error)
            await ctx.channel.send("An internal error has occured")

    @commands.command(
        aliases=['end', 'stop'],
        help="Stops the current conversation with ChatGPT.",
        brief="Stops the current conversation with ChatGPT."
        )
    async def KillThread(self, ctx):
            
        current_channel = str(ctx.guild.id) + ',' + str(ctx.channel.id)
        for ch in self.active_thread.keys():
            if ch == current_channel:
                del self.active_thread[ch]
                await ctx.send('Ending thread. Thanks for the conversation.')
                return
        await ctx.send('Sorry, but the conversation never began.')

async def setup(bot):
    await bot.add_cog(DeepChat(bot))


def edit_responce(response):
    split_response = response.split("</think>")
    if len(split_response) == 2:
        text_thought, text_main = split_response
    else:
        text_thought = split_response[0]
        text_main = ''
    
    text_thought = text_thought.removeprefix("<think>")
    text_thought = text_thought.strip()
    
    text_main = text_main.strip()
    
    return text_main, text_thought

class DeepMessage(dui.View):
    def __init__(self, thought: str):
        super().__init__()
        self.thought = thought
        
    @dui.button(label="Thinking...")
    async def thoughtBtn(self, interaction, button):
        await interaction.response.send_message(self.thought, ephemeral=True)
        