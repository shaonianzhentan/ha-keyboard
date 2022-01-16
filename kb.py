import keyboard, json, time, os, hashlib, uuid, socket
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

# 获取yaml文件数据
def getConfig():
    data = {}
    yaml_path = os.path.join(os.path.abspath("."), "kb.yaml")
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
        keyboard.on_release(self.on_release)

    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode('utf-8'))
        # 自动发现配置
        if msg.topic == discovery_topic and payload == 'online':
            self.key_record = {}

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("On Subscribed: qos = %d" % granted_qos)

    def on_disconnect(self, client, userdata, rc):
        print("Unexpected disconnection %s" % rc)

    def get_unique_id(self, name, action):
        return md5(f'ha_keyboard-{name}{action}')

    # 自动配置
    def discover(self, name, action):
        unique_id = self.get_unique_id(name, action)
        device_info = {
            "name": "键盘控制",
            "configuration_url": "",
            "identifiers": [ identifiers ],
            "model": IP,
            "sw_version": "1.1",
            "manufacturer":"shaonianzhentan"
        }
        param = {
            "automation_type": "trigger",
            "topic": f"ha_keyboard/{unique_id}",
            "type": action,
            "subtype": name,
            "device": device_info
        }
        self.client.publish(f"homeassistant/device_automation/{unique_id}/config", payload=json.dumps(param), qos=0)
        # 添加传感器
        self.client.publish(f"homeassistant/sensor/{md5(identifiers)}/config", payload=json.dumps({
            "name": device_info['name'],
            "state_topic": f"ha_keyboard/{IP}",
            "device": device_info
        }), qos=0)

    def publish(self, name, action):
        unique_id = self.get_unique_id(name, action)
        self.client.publish(f"ha_keyboard/{unique_id}", payload='', qos=0)
        # 更新传感器
        self.client.publish(f"ha_keyboard/{IP}", payload=name, qos=0)

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

HaKeyboard()