# MosGotTrans bot

## Install & Update

install service

    sudo cp scripts/mosgortrans.service /etc/systemd/system

```bash
cd ~/PycharmProjects/mosgortrans
sudo systemctl stop mosgortrans.service
git pull balshgit master
sudo cp ~/Pycharmprojects/mosgortrans/* /opt/mosgortrans/ -r
sudo systemctl start mosgortrans.service
```

## Clean

```bash
killall geckodriver
killall firefox
killall python
```
