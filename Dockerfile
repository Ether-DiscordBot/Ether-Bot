FROM python:latest

COPY . /mochi
RUN pip install -r ./mochi/requirements.txt

WORKDIR /mochi

CMD ["python", "-m", "mochi"]
