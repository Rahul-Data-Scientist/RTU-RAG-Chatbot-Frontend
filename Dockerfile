# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app (excluding files in .dockerignore)
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "streamlit_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
