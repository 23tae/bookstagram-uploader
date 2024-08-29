FROM python:3.12-slim

RUN apt-get update && apt-get install -y tzdata

ENV TZ=Asia/Seoul

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
