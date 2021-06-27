FROM python:latest
WORKDIR /
COPY .
CMD ["test.py"]
