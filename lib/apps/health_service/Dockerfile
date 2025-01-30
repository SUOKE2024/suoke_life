FROM ubuntu:latest

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y curl

CMD ["echo", "Health Service Dockerfile"] 