FROM ubuntu:22.04 AS builder

# TODO: Find Version for Linux Kernel Headers
# When I run the `dpkg -l linux-kernel-headers` it shows a None Version?

RUN apt update && \
    apt install -y \
    git=1:2.34.1-1ubuntu1.15 \
    wget=1.21.2-2ubuntu1.1 \
    tar=1.34+dfsg-1ubuntu0.1.22.04.2 \
    linux-kernel-headers \
    build-essential=12.9ubuntu3 \
    libpcre++-dev=0.9.5-7 \
    zlib1g-dev=1:1.2.11.dfsg-2ubuntu9.2

ENV NGINX_VERSION 1.19.7


RUN wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz -O /tmp/nginx-${NGINX_VERSION}.tar.gz && \
    cd /tmp && \
    tar -xvzf nginx-${NGINX_VERSION}.tar.gz

# TODO: Likely need to remove the no-check-certificate
RUN wget https://github.com/simpl/ngx_devel_kit/archive/v0.3.3.tar.gz --no-check-certificate -O /tmp/ngx_devel_kit-0.3.3.tar.gz && \
    cd /tmp && \
    tar -xvzf ngx_devel_kit-0.3.3.tar.gz 

# TODO: Likely need to remove the no-check-certificate
RUN wget https://github.com/openresty/set-misc-nginx-module/archive/v0.33.tar.gz --no-check-certificate  -O /tmp/set-misc-nginx-module-0.33.tar.gz && \
    cd /tmp && \
    tar -xvzf set-misc-nginx-module-0.33.tar.gz

RUN cd /tmp/nginx-${NGINX_VERSION} && \
    ./configure --with-compat --with-http_sub_module --add-dynamic-module=/tmp/ngx_devel_kit-0.3.3 --add-dynamic-module=/tmp/set-misc-nginx-module-0.33 && \
    make && \
    make install && \
    make modules


FROM nginx:1.19.7-alpine

# For Versioning
ARG TAG
ARG DATA_BUNDLE
ARG OUTCOME_TOOLKIT_RELEASE
ARG ROUTING_DIR=default
ARG API_HOST_URI=/api/
ENV DATA_BUNDLE=$DATA_BUNDLE
ENV TAG=$TAG
ENV OUTCOME_TOOLKIT_RELEASE=$OUTCOME_TOOLKIT_RELEASE
ENV ROUTING_DIR=$ROUTING_DIR
ENV API_HOST_URI=$API_HOST_URI

# Source: https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask

# Add bash for boot cmd
RUN apk add bash \
    --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/v3.14/main \
    ca-certificates


COPY --from=builder /tmp/nginx-${NGINX_VERSION}/objs/* /etc/nginx/modules/

COPY --from=builder /usr/local/lib/* /lib/x86_64-linux-gnu/

# Add nginx.conf to container
COPY --chown=nginx:nginx start.sh /app/start.sh
COPY --chown=nginx:nginx templates /etc/nginx/templates

# set workdir
WORKDIR /app

# permissions and nginx user for tightened security
RUN chown -R nginx:nginx /app && chmod -R 755 /app && \
        chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chmod -R 755 /var/log/nginx; \
        chown -R nginx:nginx /etc/nginx/conf.d && \
        chown -R nginx:nginx /etc/nginx
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid

# # Uncomment to keep the nginx logs inside the container - Leave commented for logging to stdout and stderr
# RUN mkdir -p /var/log/nginx
# RUN unlink /var/log/nginx/access.log \
#     && unlink /var/log/nginx/error.log \
#     && touch /var/log/nginx/access.log \
#     && touch /var/log/nginx/error.log \
#     && chown nginx /var/log/nginx/*log \
#     && chmod 644 /var/log/nginx/*log

USER nginx

# Default Health Checks
# WARNING: If you update this section make sure to update the task definition template. 
# AWS does not use health checks defined in the image definition and so health checks need to be redifiened in the task definiton as well
# PAIRED FILE: 'deployments/outcome-toolkit-all-task-definition-template.json'
HEALTHCHECK \
    --interval=10s \
    --timeout=10s \
    --start-period=300s \
    --retries=10 \
    CMD curl --silent --fail localhost:${NGINX_LISTEN_PORT}/health-check || exit 1

# Intented Ports
EXPOSE 8080

# Default CMD
CMD /app/start.sh
