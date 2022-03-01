FROM python:3.9-alpine as builder

RUN apk add --no-cache git build-base

WORKDIR /app
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN git clone https://github.com/taransergey/ddoser.git /app
RUN pip3 install -r requirements.txt
ADD ./docker-entrypoint.sh .
RUN chmod +x ./docker-entrypoint.sh

FROM python:3.9-alpine

RUN apk add --no-cache git
WORKDIR /app

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

ENTRYPOINT ["./docker-entrypoint.sh"]
