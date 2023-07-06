FROM ubuntu:22.04

RUN apt-get update && apt-get install -y socat

RUN useradd ctf

WORKDIR /service

RUN mkdir ./data && chown ctf:ctf ./data && chmod 700 ./data

COPY ./server .
RUN chmod 555 ./server

USER ctf

CMD ["socat", "TCP-LISTEN:9999,reuseaddr,fork", "EXEC:timeout 300 ./server"]
