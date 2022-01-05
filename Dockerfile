FROM python:3.10.1

WORKDIR /ether

COPY . /ether
RUN pip install -r ./requirements.txt

CMD ["python", "-u", "-m", "ether"]
