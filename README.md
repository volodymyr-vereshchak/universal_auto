# Universal Auto
This repo is supposed to get statistics from Uber, Bold, Uklon to calculate performance of car cross this aggregators for fleet owners and provide reports via telegram bit for Drivers, Fleet Managers and Fleet Owners. 

# How to run weekly report and see results in console without Selenium?
```
python manage.py runscript weekly
```

# How to run a project on your local machine?
First of all you need create a telegram bot using https://t.me/BotFather and get TELEGRAM_TOKEN and export it to ENV variable in your console like:

```
export TELEGRAM_TOKEN=your token here
```

after run to start web server and your telgram bot:

```
honcho start
```

# How to start contribute?

1. Take an issue from the list  https://github.com/SergeyKutsko/universal_auto/issues and ask questions
2. Create a new branch from a master branch with the name in the format: issues-12-your_last_name
3. After work is finished and covered by tests create a Pull Request with good description what exactly you did and how and add Sergey Kutsko as reviewer. 
4. After review fix found problems
5. Manual QA stage need to be done by other person to confirm solutions works as expected
6. We will deploy to staging server to confirm it works in pre-pod ENV
7. Merge into master and deploy to production instance. 
