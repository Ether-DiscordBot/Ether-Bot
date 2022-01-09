FROM python:3.8

WORKDIR /ether

COPY . /ether
RUN pip install -r ./requirements.txt

CMD ["python", "-u", "-m", "ether"]
