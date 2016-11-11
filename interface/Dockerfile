FROM debian:8.1

# install mysql, python, dependencies for pip modules
RUN apt-get -y update && apt-get -y install \
    python python-pip python-dev build-essential \
    libldap2-dev libsasl2-dev libssl-dev libmysqlclient-dev

COPY app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# run
WORKDIR /code/app
CMD ["bash", "/code/extra/cmd.sh"]
