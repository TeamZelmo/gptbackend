FROM python:3.10-slim

# System dependencies install karna jo Playwright ke liye zaroori hain
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apts/lists/*

WORKDIR /app

# Requirements file copy karke dependencies install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r rq.txt

# Playwright ke browsers aur system dependencies install karein
RUN playwright install --with-deps

# Baaki sara code copy karein
COPY . .

# Cloud environments ke liye port 8000 expose karein
EXPOSE 8000

# App run karne ki command (headless mode zaroori hai servers ke liye)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
