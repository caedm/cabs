FROM debian:8.1

RUN echo mysql-server mysql-server/root_password password mypassword \
        | debconf-set-selections
RUN echo mysql-server mysql-server/root_password_again password mypassword \
        | debconf-set-selections

# install mysql, python, dependencies for pip modules
RUN apt-get -y update && apt-get -y install mysql-server \
    python python-pip python-dev build-essential libmysqlclient-dev \
    libldap2-dev libsasl2-dev libssl-dev

COPY app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# run
RUN sed -i 's/^bind-address/#bind-address/' /etc/mysql/my.cnf
ENTRYPOINT ["/code/extra/entrypoint.sh"]
WORKDIR /code/app

# cabsbroker will start automatically, but you can also stop and start it again
# without exiting the container.
CMD ["bash", "-c", "./cabsbroker.py --debug ; bash"]
