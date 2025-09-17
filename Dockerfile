FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY aeb ./aeb
COPY service.py ./service.py

# ---- Security Hardening ----
# Create unprivileged user instead of running as root (addresses hotspot)
RUN useradd -u 1001 -r -s /sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "service.py"]