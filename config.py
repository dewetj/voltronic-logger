##### TEST OR LIVE ######
testing = True

##### Program log  #####
log_info = True
log_warning = True
log_location = "log.txt" #for Linux use someting like /usr/voltronic-logger/log.txt

##### Logging Interval #####
logging_interval = 5

##### Database Configs  #####
db_active = False
db_string = "postgres://live_user:live_password@someprovider_url/live_db"

##### MQTT Configs  #####
# Turn MQTT on or off
mqtt_active = True
mqtt_publish_topic = "/garage/inverter"
mqtt_broker = "127.0.0.1"
mqtt_username = "mqtt-username"
mqtt_password = "mqtt_password"
mqtt_subscribe_topic = "/garage/inverter/command"
mqtt_retry_limit = 20

# Use test links
if testing == True:
    mqtt_publish_topic = "/location/test"
    mqtt_subscribe_topic = "/location/test/command"
    db_string = "postgres://test_user:test_password@someprovider_url/test_db"
