FROM python:3.13.10-slim-trixie

COPY ./src /src

RUN mkdir -p /etc/bmdns
RUN mkdir -p /var/log/bmdns/

COPY ./conf/sample_conf.yaml /bmdns_conf.yaml

RUN pip install pyyaml
EXPOSE 53/udp

RUN printf "cp -n /bmdns_conf.yaml /etc/bmdns/conf.yaml\ntouch /var/log/bmdns/bmdns.log\npython3 -u /src/main.py" > /entrypoint.sh

CMD ["bash", "/entrypoint.sh"]