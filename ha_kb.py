import keyboard, json, time, os, hashlib, uuid, socket, sys
import paho.mqtt.client as mqtt

def get_mac_address(): 
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:] 
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip

MAC = get_mac_address()
IP = get_host_ip()
identifiers = f'ha-keyboard-{MAC}'

# MD5加密
def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

discovery_topic = "homeassistant/status"
subscribe_topic = md5(f'{identifiers}{IP}')

# 获取yaml文件数据
def getConfig():
    data = { 'mqtt': {} }
    yaml_path = os.path.join(os.path.abspath("."), "ha_kb.yaml")
    if os.path.exists(yaml_path):
        file = open(yaml_path, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        import yaml
        data = yaml.full_load(file_data)
    return data

class HaKeyboard():

    def __init__(self):
        # 按键记录
        self.key_record = {}
        self.config = getConfig()
        client_id = "ha_keyboard"
        config_mqtt = self.config['mqtt']
        HOST = config_mqtt.get('host', 'localhost')
        PORT = config_mqtt.get('port', 1883)
        USERNAME = config_mqtt.get('user', '')
        PASSWORD = config_mqtt.get('password', '')

        self.device_info = {
            "name": "键盘控制",
            "configuration_url": "https://github.com/shaonianzhentan/ha-keyboard",
            "identifiers": [ identifiers ],
            "model": MAC,
            "sw_version": IP,
            "manufacturer":"shaonianzhentan"
        }

        client = mqtt.Client(client_id)
        self.client = client
        client.username_pw_set(USERNAME, PASSWORD)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_subscribe = self.on_subscribe
        client.on_disconnect = self.on_disconnect
        client.connect(HOST, PORT, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(discovery_topic)
        client.subscribe(subscribe_topic)
        keyboard.on_release(self.on_release)
        self.discover_sensor()

    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode('utf-8'))
        # 自动发现配置
        if msg.topic == discovery_topic and payload == 'online':
            self.key_record = {}
            self.discover_sensor()
        elif msg.topic == subscribe_topic:
            # 获取当前解释器路径
            p = sys.executable
            # 启动新程序(解释器路径, 当前程序)
            os.execl(p, p, *sys.argv)
            # 关闭当前程序
            sys.exit()

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    def on_disconnect(self, client, userdata, rc):
        print("Unexpected disconnection %s" % rc)

    def get_unique_id(self, name, action):
        return md5(f'ha_keyboard-{name}{action}')

    # 自动配置
    def discover(self, name, action):
        unique_id = self.get_unique_id(name, action)
        param = {
            "automation_type": "trigger",
            "topic": f"ha_keyboard/{unique_id}",
            "type": action,
            "subtype": name,
            "device": self.device_info
        }
        self.client.publish(f"homeassistant/device_automation/{unique_id}/config", payload=json.dumps(param), qos=0)

    def discover_sensor(self):
        # 添加传感器
        name = self.device_info['name']
        unique_id = self.get_unique_id(name, '')
        self.client.publish(f"homeassistant/sensor/{unique_id}/config", payload=json.dumps({
            "name": name,
            "icon": "mdi:keyboard",
            "unique_id": unique_id,
            "state_topic": f"ha_keyboard/{IP}",
            "json_attr_t": f"ha_keyboard/{IP}/attr",
            "device": self.device_info
        }), qos=0)

        button_name = f'重启{name}服务'
        unique_id = self.get_unique_id(button_name, '')
        self.client.publish(f"homeassistant/button/{unique_id}/config", payload=json.dumps({
            "name": button_name,
            "unique_id": unique_id,
            "command_topic": subscribe_topic,
            "payload_press": "restart",
            "device": self.device_info
        }), qos=0)

    def publish(self, name, action):
        unique_id = self.get_unique_id(name, action)
        self.client.publish(f"ha_keyboard/{unique_id}", payload='', qos=0)

    def on_release(self, ev):
        key = f'{ev.name}{ev.scan_code}'
        key_record = self.key_record.get(key)
        name = f'键码 {ev.scan_code}'
        action = f'键名 {ev.name}'
        # 初次按键
        if key_record is None:
            print('初次按键')
            self.discover(name, action)
            self.key_record[key] = True
        print(name, action)
        self.publish(name, action)
        # 更新传感器
        self.client.publish(f"ha_keyboard/{IP}/attr", payload=json.dumps({
            'device': ev.device,
            "key_name": ev.name,
            "key_code": ev.scan_code
        }), qos=0)
        self.client.publish(f"ha_keyboard/{IP}", payload=time.strftime('%H:%M:%S', time.localtime()), qos=0)

HaKeyboard()