# Use an official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the container
COPY requirements.txt /app/

# Install any needed dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files to the container
COPY . /app/

# Set the environment variable for the virtual environment
ENV VIRTUAL_ENV=/app/venv

# Create a virtual environment inside the container
RUN python -m venv $VIRTUAL_ENV

# Activate the virtual environment and install the dependencies
RUN $VIRTUAL_ENV/bin/pip install --no-cache-dir -r requirements.txt

# Set the virtual environment as the default Python interpreter
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Expose the port the app runs on (if needed)
EXPOSE 8000  

# Change this depending on your app

# Run the application (adjust this command based on your entry point)
CMD ["python", "main.py"] 

# Replace app.py with your entry script
