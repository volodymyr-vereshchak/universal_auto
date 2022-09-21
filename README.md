# universal_auto
This repo is supposed to get statistics from Uber, Bold, Uklon to calculate performance of car cross this aggregators for fleet owners.

# How to run report and see results in console?
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
