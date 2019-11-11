from paho.mqtt.publish import single as publish
from paho.mqtt.subscribe import simple as subscribe
from func_timeout import func_timeout, FunctionTimedOut

from mqtt_listener import MQTTListener


BROKER_HOST = '127.0.0.1'
BROKER_PORT = 1883




def test_can_connect_to_broker():
    listener = MQTTListener(
        topic='test',
        on_message=lambda: None,
        broker_host=BROKER_HOST,
        broker_port=BROKER_PORT
    )
    listener.connect()
    assert listener.connected

    listener.disconnect()

def test_can_disconnect_from_broker():
    listener = MQTTListener(
        topic='test',
        on_message=lambda: None,
        broker_host=BROKER_HOST,
        broker_port=BROKER_PORT
    )
    listener.connect()
    was_connected = listener.connected

    listener.disconnect()

    assert was_connected and not listener.connected

def test_on_message_called_on_recieve():
    topic = 'test_on_message_called_on_recieve'
    rx_topic = 'on_message_called'

    def on_message(*args, **kwargs):
        publish(
            topic=rx_topic,
            payload='payload',
            qos=1,
            hostname=BROKER_HOST,
            port=BROKER_PORT
        )

    listener = MQTTListener(
        topic=topic,
        on_message=on_message,
        broker_host=BROKER_HOST,
        broker_port=BROKER_PORT
    )
    listener.connect()

    publish(
        topic=topic,
        payload='payload',
        qos=1,
        hostname=BROKER_HOST,
        port=BROKER_PORT
    )

    try:
        func_timeout(
            timeout=3,
            func=subscribe,
            kwargs={
                'topics': rx_topic,
                'qos': 1,
                'hostname': BROKER_HOST,
                'port': BROKER_PORT,
            }
        )
    except FunctionTimedOut:
        on_message_called = False
    else:
        on_message_called = True

    assert on_message_called
