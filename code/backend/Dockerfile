FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openblas-dev \
    gfortran \
    libc-dev \
    g++ \
    libstdc++ \
    openblas \
    glib \
    cairo \
    pango \
    gdk-pixbuf \
    && rm -rf /var/cache/apk/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn-worker

RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app

COPY --chown=appuser:appuser . .

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

WORKDIR /app

# Run gunicorn with uvicorn workers
# Use -u flag to make stdout/stderr unbuffered so logs appear immediately
CMD ["python", "-u", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

