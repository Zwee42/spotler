FROM python:3.13-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl bash && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Setup backend
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Setup frontend
COPY frontend/package*.json frontend/
RUN cd frontend && npm install

# Copy source code
COPY backend/ backend/
COPY frontend/ frontend/

# Build frontend
RUN cd frontend && npm run build

# Copy start script
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8000 5173 4173

CMD ["./start.sh"]