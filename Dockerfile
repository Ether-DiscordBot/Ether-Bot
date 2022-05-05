FROM python:3.10.3

WORKDIR /ether

COPY . /ether
RUN pip install -r ./requirements.txt

CMD ["python", "-u", "-m", "ether"]