# ha-keyboard
键盘监听


[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
![visit](https://visitor-badge.laobi.icu/badge?page_id=shaonianzhentan.ha-keyboard&left_text=visit)

## 安装

下载源代码
```bash
git clone https://github.com/shaonianzhentan/ha-keyboard
```
安装依赖
```bash
cd ha-keyboard

sudo pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```
安装失败则需要安装编译工具
```bash
sudo pip install --upgrade setuptools
```
## 启动
```bash
sudo python3 ha_kb.py
```


## 开机启动

生成系统启动文件
```bash
sudo nano /etc/systemd/system/ha_kb.service
```
文件内容（**WorkingDirectory需修改为对应目录**）
```
[Unit]
Description=ha-keyboard
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ha_kb.py
WorkingDirectory=/root/git/ha-keyboard/
RestartSec=15
Restart=always

[Install]
WantedBy=multi-user.target
```
启动服务
```bash
sudo systemctl start ha_kb
```
加入开机项
```bash
sudo systemctl enable ha_kb
```
重启服务
```bash
sudo systemctl restart ha_kb
```
查看运行状态
```bash
sudo systemctl status ha_kb
```

## 调试

```yaml
service: logger.set_level
data:
  homeassistant.components.mqtt: debug
```

```yaml
service: logger.set_level
data:
  homeassistant.components.mqtt: warn
```


## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|  |支付宝|微信|
|---|---|---|
奶茶= | <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat.png" height="160" width="160" alt="微信支付" title="微信">

## 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat-channel.png" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理">

---
**在使用的过程之中，如果遇到无法解决的问题，付费咨询请加Q`635147515`**