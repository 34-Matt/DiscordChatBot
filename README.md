# Discord Chatbot

Making a chatbot interface for my friends on Discord.

## Installation
There are three main steps before the bot can be used.
First, the `.env` file needs to be created, this all the tokens and urls needed to run the bot.
The file should contain the following:

``` text
DISCORD_TOKEN=__Discord_Token__
OPENAI_TOKEN=__Openai_Token__
OLLAMA_URL=__OLLAMA_URL__
```

Replace `__Discord_Token__` with the discord token to connect your bot to discord. Replace `__Openai_Token__` with the OpenAI token to connect to the OpenAI API (if not using, replace with a temp string). Finally, replace `__OLLAMA_URL__` with the Ollama url to connect to (again, if not using, replace with a temp string).

The second step is to initialize the python environment. This can be done with:

```bash
pip install -r requirements.txt
```

Finally, run the script with:

```bash
python ChatBot.py
```

## Additional setup
Currently, the bot is setup to run Deepseek through Ollama. In the `ChatBot.py` file, this was setup on line 24 with
```python
for cog in cogs.ollama_cogs:
```
to use the GPT catalog, use the following:
```python
for cog in cogs.GPT_cogs:
```