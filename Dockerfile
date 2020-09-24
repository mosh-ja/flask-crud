FROM python:3.8.5

RUN mkdir /app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "/app/src/server.py"]