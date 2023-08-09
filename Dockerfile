# python application with version 3.10.6 
# use latest to install latest python

FROM python:3.10.6

WORKDIR /app

# copy requirements.txt to the docker container
COPY requirements.txt requirements.txt

# upgrade pip
RUN pip install --upgrade pip
# install required packages in docker container
RUN pip install -r requirements.txt

COPY . .

# Run application
CMD ["python3", "main.py"]


# use command 'docker image build -t <image-name>:version .' to build docker container.
# and run the container using command "docker run <image-name>"