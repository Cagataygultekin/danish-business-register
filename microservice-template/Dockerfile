FROM python:3.8-slim-buster

WORKDIR /microservice-template

# Install git
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean

# Add German locale
RUN apt-get clean && apt-get update

# Install gunicorn for serving the API
RUN python -m pip install gunicorn

# copy all - tailor to the current working directory
COPY . /microservice-template

# Install any needed packages specified in requirements.txt
RUN python -m pip install -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run gunicorn when the container launches -w -> number of worker
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "5", "--timeout", "3600", "run:app"]
