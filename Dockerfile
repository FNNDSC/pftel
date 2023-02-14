#
# Dockerfile for pfdcm.
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build --build-arg UID=$UID -t local/pftel .
#
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pftel .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pftel
#
# To pass an env var HOST_IP to the container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pftel
#
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

LABEL DEVELOPMENT="                                                        \
    docker run --rm -it                                                    \
    -p 22223:22223 \
    -v $PWD/pftel:/app:ro  local/pftel /start-reload.sh                    \
"

ENV DEBIAN_FRONTEND=noninteractive


COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt && rm -v /tmp/requirements.txt
RUN pip install https://github.com/msbrogli/rpudb/archive/master.zip
RUN pip install tzlocal
COPY ./pftel /app

RUN apt update                              && \
    apt-get install -y apt-transport-https  && \
    apt -y install vim telnet netcat procps

ENV PORT=22223
EXPOSE ${PORT}
