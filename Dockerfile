FROM zenika/alpine-chrome:with-node
USER root
RUN apk add --no-cache python3 py3-pip; \
    npm install --production single-file-cli; \
    pip3 install aiolinkding apprise; \
    ln -s /usr/src/app/node_modules/single-file-cli/single-file /usr/local/bin/single-file; \
    mkdir /archives; \
    echo "*/60 * * * * /usr/bin/python3 /opt/check.py >> /var/log/archiver.log" >> /var/spool/cron/crontabs/root
VOLUME /archives
COPY check.py /opt/
WORKDIR /archives
CMD crond -f