FROM nestybox/ubuntu-bionic-systemd-docker

WORKDIR /root

RUN (echo 'root'; echo 'root') | passwd root \
    && mkdir /root/.ssh \
    && chown root:root /root/.ssh \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

COPY services/ .
