##### TEST OR LIVE ######
testing = True

##### Database Configs  #####
if testing == False:
    db_string = "postgres://live_user:live_password@someprovider_url/live_db"
else:    
    db_string = "postgres://test_user:test_password@someprovider_url/test_db"

##### MQTT Configs  #####
# Turn MQTT on or off
mqtt_active = True
mqtt_topic = "/garage/inverter"
mqtt_broker = "127.0.0.1"
mqtt_username = "mqtt-username"
mqtt_password = "mqtt_password"

# Publish to test topic
if testing == True:
    mqtt_topic = "/garage/test"
