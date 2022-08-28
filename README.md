# MosGotTrans bot
Бот для получения расписания конкретных автобусов для конкретных остановок

## Install & Update

install service

    sudo cp scripts/mosgortrans.service /etc/systemd/system

```bash
cd ~/PycharmProjects/mosgortrans
sudo systemctl stop mosgortrans.service
git pull balshgit master
udo rsync -a --delete --progress ~/mosgortrans/* /opt/mosgortrans/ --exclude .git
sudo systemctl start mosgortrans.service
```

## Clean

```bash
killall geckodriver
killall firefox
killall python
```

## Tests
docker-compose run bot python -m pytest tests/bot/test_bot.py::test_selenoid_text

## Help article

[Пишем асинхронного Телеграм-бота](https://habr.com/ru/company/kts/blog/598575/)

[fast_api_aiogram](https://programtalk.com/vs4/python/daya0576/he-weather-bot/telegram_bot/dependencies.py/)

## TODO

- [x] Добавить очередь сообщений
- [x] Исправить запуск локально
- [ ] Добавить тестов
- [x] Close connection
