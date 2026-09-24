#!/bin/bash

bash /docker-entrypoint.d/20-envsubst-on-templates.sh
mv /etc/nginx/conf.d/nginx.conf /etc/nginx/nginx.conf
nginx -g 'daemon off;'
