import tiktoken
from discord.ext import commands

DEFAULT_ENCODING = tiktoken.encoding_for_model("text-davinci-003")

def selectEncoding(name):
    return tiktoken.get_encoding(name)

def getTokens(text, encoding = DEFAULT_ENCODING):
    return encoding.encode(text)

def revertTokens(token, encoding = DEFAULT_ENCODING):
    return encoding.decode(token)

def extractTokenInfo(text, encoding = DEFAULT_ENCODING):
    token = getTokens(text, encoding)
    return len(token), [encoding.decode_single_token_bytes(t) for t in token]

class MyChannel:
    def __init__(self, ctx:commands.Context):
        self.guild = ctx.guild
        self.channel = ctx.channel
        
        
    def __eq__(self, ctx):
        if isinstance(ctx, commands.Context) or isinstance(ctx, MyChannel):
            return self.guild == ctx.guild and self.channel == ctx.channel
        else:
            return False