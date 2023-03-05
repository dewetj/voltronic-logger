import time
import config

from helpers import *
from models import *

# instantiate the class
db = Elephant_db()
if config.mqtt_active == True:
    mqtt = Mqtt()

while True:
    qpigs_list = execute_command('QPIGS')
    qmod_list = execute_command('QMOD')
    qpigs_list.append(qmod_list[0][0:1])
    # Convert to a tuple and insert into Postgres DB
    mapped_data = map_datatypes(qpigs_list)
    row = tuple(mapped_data) 
    db.insert(row)
    # Convert to a dictionary and publish to MQTT
    if config.mqtt_active == True:
        mqtt.publish(create_dict(mapped_data))
        time.sleep(5)