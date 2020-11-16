FROM nginxinc/nginx-unprivileged:latest

RUN mkdir /etc/nginx/certs && chown nginx /etc/nginx/certs

ADD default.conf /etc/nginx/conf.d/default.conf
