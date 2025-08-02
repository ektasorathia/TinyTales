FROM hub.tess.io/tess/ubuntu-22.04:hardened AS packer

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
RUN apt -y upgrade && apt update && \
    apt install -y libsnappy-dev python3.11 python3-pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives  --set python3 /usr/bin/python3.11

RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY pip.conf .
ENV PIP_CONFIG_FILE=/app/pip.conf

COPY pyproject.toml .
COPY src ./src

RUN pip install .
# RUN pip install ".[dev]" # use for local development only

RUN for i in `find / -perm /6000 -type d 2> /dev/null`; do chmod a-s $i; done

EXPOSE 8080
CMD ["uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8080"]