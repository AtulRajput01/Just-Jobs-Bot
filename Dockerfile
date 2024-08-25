# Use Python 3.9 or later version as base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and requirements-dev.txt first
COPY requirements.txt requirements-dev.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements-dev.txt

# Copy the rest of the application code
COPY . /app/

# Command to run the bot
CMD ["python", "justjobs.py"]
