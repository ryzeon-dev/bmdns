FROM python:3.13

COPY ./src /src

RUN mkdir -p /etc/bmdns
RUN mkdir -p /usr/local/share/bmdns/

COPY ./conf/sample_conf.yaml /bmdns_conf.yaml

RUN pip install pyyaml
EXPOSE 53

RUN printf "cp -n /bmdns_conf.yaml /etc/bmdns/conf.yaml\npython3 -u /src/main.py" > /entrypoint.sh

CMD ["bash", "/entrypoint.sh"]