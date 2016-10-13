FROM centos:7

# python + dependencies
RUN yum -y install epel-release
RUN yum -y install python-pip python-devel libffi-devel openssl-devel
RUN yum -y groupinstall development
COPY app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# install mock who program
COPY extra/who.sh /usr/bin/who
RUN touch /tmp/users.txt
RUN chmod +x /usr/bin/who

# install cabs
COPY ./app/ /tmp/agent
RUN /tmp/agent/install.sh && rm -r /tmp/agent

# run
COPY extra/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
