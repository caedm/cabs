FROM debian:8.1

RUN apt-get -y update && apt-get -y upgrade

# mysql
RUN echo mysql-server mysql-server/root_password password mypassword \
        | debconf-set-selections
RUN echo mysql-server mysql-server/root_password_again password mypassword \
        | debconf-set-selections
RUN apt-get -y update && apt-get -y install mysql-server


#COPY . /broker
#RUN /broker/scripts/install.sh
