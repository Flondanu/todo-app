FROM python:3.12-slim
 
WORKDIR /app
 
# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy app code
COPY . .
 
# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
 
EXPOSE 5000
 
# Use gunicorn in production, flask dev server locally
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
