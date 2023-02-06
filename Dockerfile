FROM python:3.10
EXPOSE 5000

#move into this folder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

#copies current folder in into current folder of image
COPY . .

#what commands should run
#each string is one part of comamand
#allows external container to make request to flask app running in container
CMD ["flask","run","--host","0.0.0.0"]