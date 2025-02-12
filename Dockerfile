# Use the official Python 3.12.9 slim image
FROM python:3.12.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building packages and handling deb files
RUN apt-get update && \
    apt-get install -y build-essential dpkg wget && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# Copy the TA-Lib deb file into the container and install the TA-Lib C library
# ------------------------------------------------------------------------------
COPY libs/ta-lib_0.6.4_amd64.deb /tmp/ta-lib.deb
RUN dpkg -i /tmp/ta-lib.deb || (apt-get update && apt-get install -f -y) && \
    rm /tmp/ta-lib.deb

# ------------------------------------------------------------------------------
# Copy the requirements file into the container
# ------------------------------------------------------------------------------
COPY requirements.txt .

# Remove the Windows-specific TA-Lib wheel line from requirements.txt.
# (Note the pattern matches "TA-Lib @" with a dash.)
RUN sed -i '/TA-Lib @/d' requirements.txt

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Install the TA-Lib Python wrapper from PyPI, which will compile against the installed TA-Lib C library
RUN pip install TA-Lib

# ------------------------------------------------------------------------------
# Copy the rest of your application code into the container
# ------------------------------------------------------------------------------
COPY . .

# Expose the default Streamlit port (8501)
EXPOSE 8501

# (Optional) Set Streamlit environment variables
ENV STREAMLIT_SERVER_ENABLE_CORS=false

# Command to run your Streamlit application
CMD ["streamlit", "run", "app.py"]
