# Cloud Run Container for Grosso Landing Page
FROM python:3.10-slim

WORKDIR /app

# Copy application files
COPY . /app

# Cloud Run defaults to PORT 8080
ENV PORT=8080
EXPOSE 8080

# Run lightweight server injecting GU_API_KEY
CMD ["python", "server.py"]
