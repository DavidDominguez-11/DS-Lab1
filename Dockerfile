# Ambiente del laboratorio: Python 3.11 + Java 17 + PySpark 3.5.1
FROM python:3.11-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk-headless procps ca-certificates tini && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"
ENV PYSPARK_PYTHON=/usr/local/bin/python

WORKDIR /opt/app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd -ms /bin/bash spark && chown -R spark:spark /opt/app
USER spark

EXPOSE 8888 4040
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--ServerApp.token=", "--notebook-dir=/opt/app"]
