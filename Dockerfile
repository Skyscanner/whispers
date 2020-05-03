FROM python:3.8.1-slim-buster

USER root
ENV HOME="/opt/whispers"
RUN useradd --home-dir $HOME --shell /bin/false user

WORKDIR $HOME
COPY . $HOME/
RUN apt update \
    && apt install -y build-essential python3-lxml python3-yaml \
    && apt clean \
    && make install \
    && chown -R user:user $HOME \
    && whispers -v

USER user
ENTRYPOINT [ "whispers" ]
