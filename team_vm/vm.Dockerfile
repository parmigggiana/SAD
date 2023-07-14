FROM nestybox/ubuntu-bionic-systemd-docker

WORKDIR /root
RUN (echo 'root'; echo 'root') | passwd root \
    && mkdir /root/.ssh \
    && chown root:root /root/.ssh \
    && echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config

COPY team_vm/start_script.sh /usr/bin
COPY team_vm/services_starter.service /lib/systemd/system/

COPY services/* .

RUN chmod +x /usr/bin/start_script.sh &&                               \
    ln -sf /lib/systemd/system/services_starter.service                    \
       /etc/systemd/system/multi-user.target.wants/services_starter.service