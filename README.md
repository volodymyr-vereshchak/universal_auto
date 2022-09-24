# universal_auto
This repo is supposed to get statistics from Uber, Bold, Uklon to calculate performance of car cross this aggregators for fleet owners.

# How to run a project on your local machine?
1. Install Docker https://docs.docker.com/engine/install/
2. Create a telegram bot using https://t.me/BotFather and get TELEGRAM_TOKEN 
3. Rename docker-compose_example.yml to docker-compose.yml
4. Replace <add your telegram token here> with token given by telegram 
5. Run `docker-compose build`
6. Run `docker-compose up`
7. Run migrations by `docker exec -it universal_auto_web_1 python manage.py migrate`
8. Open http://localhost:8080/ in browser

# How to run report and see results in console?
```
docker exec -it universal_auto_web_1 python manage.py runscript weekly
```

