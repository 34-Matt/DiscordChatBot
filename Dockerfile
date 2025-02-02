FROM python:latest

WORKDIR /home

COPY DiscordOpenAi.py /home/
COPY util.py /home/
COPY .env /home/
COPY cogs /home/cogs
COPY requirements.txt /home/

RUN pip install -r requirements.txt

CMD [ "python", "./DiscordOpenAi.py" ]