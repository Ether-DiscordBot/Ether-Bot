FROM python:3.11.0

WORKDIR /ether

COPY . /ether
RUN pip install -r ./requirements.txt

CMD ["python", "-u", "-m", "ether"]