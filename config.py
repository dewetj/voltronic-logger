##### TEST OR LIVE ######
testing = True

##### Database Configs  #####
db_active = True
db_string = "postgres://live_user:live_password@someprovider_url/live_db"

##### MQTT Configs  #####
# Turn MQTT on or off
mqtt_active = True
mqtt_publish_topic = "/garage/inverter"
mqtt_broker = "127.0.0.1"
mqtt_username = "mqtt-username"
mqtt_password = "mqtt_password"
mqtt_subscribe_topic = "/garage/inverter/command"

# Use test links
if testing == True:
    mqtt_publish_topic = "/garage/test"
    mqtt_subscribe_topic = "/garage/test/command"
    db_string = "postgres://test_user:test_password@someprovider_url/test_db"
