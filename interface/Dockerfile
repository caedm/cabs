FROM debian:8.1

# install mysql, python, dependencies for pip modules
RUN apt-get -y update && apt-get -y install \
    python python-pip python-dev build-essential apache2 \
    libldap2-dev libsasl2-dev libssl-dev libmysqlclient-dev

COPY app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN apt-get -y install libmysqlclient-dev
RUN pip install django-auth-ldap MySQL-python

# install cabs interface
RUN apt-get -y install libapache2-mod-wsgi
COPY ./app /tmp/app
RUN /tmp/app/install.sh && rm -r /tmp/app

# run
WORKDIR /opt/cabsinterface
COPY extra/cmd.sh /cmd.sh
CMD ["bash", "/cmd.sh"]
