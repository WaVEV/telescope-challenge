FROM mcr.microsoft.com/playwright/python:v1.35.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Add your application code
COPY . .

# Set the command to run your application
CMD [ "python", "main.py" ]
