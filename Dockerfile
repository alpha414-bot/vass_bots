# docker build -t selenium-bot .
FROM python:3.11-slim

# Copy requirements file into the image
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r /app/requirements.txt

# Copy the rest of the app code
COPY . /app/

# Set the working directory
WORKDIR /app

# Command to run the bot
CMD ["python", "main.py"]
