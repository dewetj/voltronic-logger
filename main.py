import time
import config

from helpers import *
from models import *

log_warning("Logger starting...")

# instantiate the class
if config.db_active == True:
    db = Elephant_db()
    log_warning("DB Active!")
if config.mqtt_active == True:
    mqtt = Mqtt()
    log_warning("MQTT Active!")

while True:
    qpigs_list = execute_command('QPIGS')
    qmod_list = execute_command('QMOD')
    qpiri_list = execute_command('QPIRI')
    combined_list = qpigs_list + qmod_list + qpiri_list
    # Convert to a tuple and insert into Postgres DB
    try:
        log_info("Mapping data...")
        mapped_data = map_datatypes(combined_list)
        log_info("Data mapped successfully!")
    except:
        log_warning("Could not map data!")
        continue
    
    if config.db_active == True:
        log_info("Inserting into DB...")
        row = tuple(mapped_data) 
        db.insert(row)
        log_info("Inserted successfully!")
    # Convert to a dictionary and publish to MQTT
    if config.mqtt_active == True:
        log_info("Publishing to MQTT...")
        mqtt.publish(create_dict(mapped_data))
        # listen for commands
        mqtt.listen()
        log_info("Published successfully!")

    # Clear processed data
    log_info("Clearing lists...")
    qpigs_list.clear()
    qmod_list.clear()
    qpiri_list.clear()
    combined_list.clear()
    log_info("Lists cleared successfully!")

    # Wait before poling again
    log_info("Sleeping...")
    time.sleep(5)