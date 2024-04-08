FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN mkdir logs
RUN touch logs/server.log logs/openai.log logs/user.log

ENV OPENAI_API_KEY=""
ENV TELEGRAM_TOKEN=""

CMD ["python", "-i", "app.py"]