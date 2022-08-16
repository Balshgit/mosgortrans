# MosGotTrans bot

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

## Help article

[Пишем асинхронного Телеграм-бота](https://habr.com/ru/company/kts/blog/598575/)

[fast_api_aiogram](https://programtalk.com/vs4/python/daya0576/he-weather-bot/telegram_bot/dependencies.py/)

## TODO

- [ ] Добавить очередь сообщений
- [ ] Исправить запуск локально
- [ ] Добавить тестов
- [ ] Close connection
