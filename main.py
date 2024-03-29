import time
import config
import platform

from helpers import *
from models import *

backup_log()
log_warning("Logger starting...")

# instantiate the class
if config.db_active == True:
    db = Elephant_db()
    log_warning("DB Active!")
if config.mqtt_active == True:
    mqtt = Mqtt()
    log_warning("MQTT Active!")
    if config.mqtt_discovery == True:
        mqtt.setupDiscovery()
        log_warning("MQTT Discovery Setup Complete!")

while True:
    # If commands timeout, an exception will be thrown and service will be restarted by daemon... Only works on linux
    if platform.system() == 'Linux':
        with Timeout(seconds=10):
            qpigs_list = execute_command('QPIGS')
            qmod_list = execute_command('QMOD')
            qpiri_list = execute_command('QPIRI')
    else:
        qpigs_list = execute_command('QPIGS')
        qmod_list = execute_command('QMOD')
        qpiri_list = execute_command('QPIRI')


    # Combine the list for all the commands
    combined_list = qpigs_list + qmod_list + qpiri_list

    # Convert to a tuple and insert into Postgres DB
    try:
        log_info("Mapping data...")
        mapped_data = map_datatypes(combined_list)
        log_info("Data mapped successfully!")
    except:
        log_warning("Could not map data!")
        log_info(str(combined_list))
        time.sleep(config.logging_interval)
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
        # Kill the process if retries keep failing...
        if mqtt.retry_count >= config.mqtt_retry_limit:
            log_warning("Retry Counter Reached, killing process!")
            raise("Kill!")
        log_info("Published successfully!")

    # Wait before poling again
    log_info("Sleeping...")
    time.sleep(config.logging_interval)