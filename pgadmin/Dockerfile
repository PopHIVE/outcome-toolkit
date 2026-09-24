FROM dpage/pgadmin4:8.5
HEALTHCHECK \
    --interval=10s \
    --timeout=5s \
    --retries=5 \
    CMD wget -O - http://localhost:80/misc/ping