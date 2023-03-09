import time
import config

from helpers import *
from models import *

# instantiate the class
if config.db_active == True:
    db = Elephant_db()
if config.mqtt_active == True:
    mqtt = Mqtt()

while True:
    qpiri_list = execute_command('QPIRI')
    print(qpiri_list)
    qpigs_list = execute_command('QPIGS')
    qmod_list = execute_command('QMOD')
    qpigs_list.append(qmod_list[0][0:1])
    # Convert to a tuple and insert into Postgres DB
    mapped_data = map_datatypes(qpigs_list)
    if config.db_active == True:
        row = tuple(mapped_data) 
        db.insert(row)
    # Convert to a dictionary and publish to MQTT
    if config.mqtt_active == True:
        mqtt.publish(create_dict(mapped_data))
        # listen for commands
        mqtt.listen()
        time.sleep(5)