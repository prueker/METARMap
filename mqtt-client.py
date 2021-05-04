import paho.mqtt.client as mqtt
import mqtt_config as config
import os

broker_url = config.broker_url
broker_port = config.broker_port
state = "OFF"

def on_connect(client, userdata, flags, rc):
   print("Connected With Result Code: {}".format(rc))

def on_message(client, userdata, message):
    decodedMessage = message.payload.decode()
    print("Message received from broker: "+ decodedMessage)
    if decodedMessage == 'ON':
        os.system('sudo python3 metar.py')
        state = "ON"
    elif (decodedMessage == 'OFF') :
        os.system('sudo ./lightsoff.sh')
        state = "OFF"

client = mqtt.Client('metarmap')
client.on_connect = on_connect
#To Process Every Other Message
client.on_message = on_message

if config.broker_username:
    client.username_pw_set(username=config.broker_username, password=config.broker_password)
client.connect(broker_url, broker_port)

client.subscribe(config.set_topic, qos=1)
client.publish(topic=config.state_topic, payload=state, qos=0, retain=False)

client.loop_forever()