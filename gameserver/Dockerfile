FROM python:3.11.4-alpine3.18

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn
COPY . .

EXPOSE 8080
CMD [ "uvicorn", "gameserver:app", "--host", "0.0.0.0", "--port", "8080" ]