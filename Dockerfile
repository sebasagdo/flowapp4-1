# Dockerfile-flask

# We simply inherit the Python 3 image. This image does
# not particularly care what OS runs underneath
FROM python:3
# Expose the port uWSGI will listen on
EXPOSE 80
MAINTAINER Flexomeno "flexomeno.com"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["run.py"]
