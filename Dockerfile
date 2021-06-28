FROM python:latest

COPY . /mochi
RUN pip install -r /Mochi-DiscordBot/requirements.txt

WORKDIR /mochi

CMD ["python", "-m", "mochi"]
