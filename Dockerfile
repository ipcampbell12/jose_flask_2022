FROM python:3.10
# EXPOSE 5000 - don't need this with gunicron

#move into this folder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

#copies current folder in into current folder of image
COPY . .

#what commands should run
#each string is one part of comamand
#allows external container to make request to flask app running in container
# CMD ["flask","run","--host","0.0.0.0"]

CMD ["/bin/bash","docker-entrypoint.sh"]

#contributing.md - show how to run dockerfile locally