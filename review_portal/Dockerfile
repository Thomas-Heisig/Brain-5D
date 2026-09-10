FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY review_portal/requirements.txt /app/review_portal/requirements.txt
RUN pip install --no-cache-dir -r /app/review_portal/requirements.txt \
    && useradd --uid 10001 --create-home reviewer \
    && mkdir -p /data && chown reviewer:reviewer /data
COPY review_portal /app/review_portal
COPY src/dashboard/static/review /app/src/dashboard/static/review
USER reviewer
EXPOSE 8766
CMD ["python", "-m", "uvicorn", "review_portal.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8766", "--no-access-log", "--limit-concurrency", "64", "--timeout-keep-alive", "5", "--no-proxy-headers"]
