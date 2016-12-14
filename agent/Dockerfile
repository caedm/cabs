FROM centos:7

# python + dependencies
RUN yum -y install epel-release
RUN yum -y install python-pip python-devel libffi-devel openssl-devel
RUN yum -y groupinstall development
COPY app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

# install mock programs
COPY extra/who.sh /usr/bin/who
RUN touch /tmp/users.txt
RUN chmod +x /usr/bin/who
COPY extra/shutdown.sh /usr/sbin/shutdown
RUN chmod +x /usr/sbin/shutdown

# run
CMD ["python", "-u", "/code/app/cabsagent.py", "--debug", "--config", "/etc/cabsagent.conf"]
