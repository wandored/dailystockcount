# Create a ubuntu base image with python 3
FROM python:3

# Set the working directory
WORKDIR /usr/src/app

# Copy all the files
COPY . .

# Install the dependencies
RUN apt-get -y update
RUN pip3 install -r ./dailystockcount/requirements.txt

# Expose the required port
EXPOSE 5000

#Run the command
CMD {"python3", "./app.py"}
