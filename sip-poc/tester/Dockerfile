FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y \
        sip-tester \
        python3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY runner.py .
COPY scenarios ./scenarios

CMD ["python3", "runner.py"]