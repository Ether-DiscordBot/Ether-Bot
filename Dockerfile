FROM python:latest

WORKDIR /mochi

COPY . /mochi
RUN pip install -r ./requirements.txt

CMD ["python", "-u", "-m", "mochi"]
