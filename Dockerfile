FROM python:3.9-slim

# Create the working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from your folder to the /app folder in the container
COPY . .

# Run the application
CMD ["python", "app.py"]