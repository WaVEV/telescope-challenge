FROM python:3.8

# Create shared folders
RUN mkdir /downloads
RUN mkdir /chromadb

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Mount the shared folders as volumes
VOLUME /downloads
VOLUME /chromadb

# Add your application code
COPY . .

# Set the command to run your application
CMD [ "python", "main.py" ]
