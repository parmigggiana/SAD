FROM python:3.11


WORKDIR /app

RUN touch valid_flags.txt

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .

CMD uvicorn main:app --host 0.0.0.0