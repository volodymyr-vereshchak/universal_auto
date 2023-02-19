FROM selenium/standalone-chrome
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN sudo apt-get update && sudo apt-get install -y \
  postgresql-contrib \
  redis-tools \ 
  python3-pip \
  python3-venv \
  python3-dev \
  python3-setuptools \
  python3-wheel \
  unzip \
  nginx
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
RUN sudo ln -sf /dev/stdout /var/log/nginx/access.log && sudo ln -sf /dev/stderr /var/log/nginx/error.log

USER nobody
RUN sudo mkdir -p /app
WORKDIR /app
COPY requirements.txt .
RUN sudo pip install -r requirements.txt
COPY . .
RUN sudo chown nobody:nogroup /app
EXPOSE 8080 44300
CMD ["honcho", "start"]