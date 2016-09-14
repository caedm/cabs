FROM debian:8.1

RUN apt-get -y update && apt-get -y upgrade

# mysql
RUN echo mysql-server mysql-server/root_password password mypassword \
        | debconf-set-selections
RUN echo mysql-server mysql-server/root_password_again password mypassword \
        | debconf-set-selections
RUN apt-get -y update && apt-get -y install mysql-server

# python
RUN apt-get -y update && apt-get install -y python python-pip
RUN apt-get -y update && apt-get install -y python-dev build-essential
RUN apt-get -y update && apt-get install -y libmysqlclient-dev
RUN apt-get -y update && apt-get install -y libldap2-dev \
                         libsasl2-dev libssl-dev
COPY res/requirements.txt /
RUN pip install -r /requirements.txt

COPY ./build/cabsbroker-7.1.5856.2/ /broker
WORKDIR /broker
RUN ./install.sh
RUN service mysql start && \
    mysql -u root -pmypassword < createdb.sql && \
    ./setupDatabase.py

CMD service mysql start && /opt/cabsbroker/cabsbroker.py
