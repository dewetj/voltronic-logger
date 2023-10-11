import psycopg2
import paho.mqtt.client as mqtt_c
import json
import config
import signal
from helpers import log_warning
from helpers import execute_command

############################################################
# Postgres DB class
############################################################
class Elephant_db:
    #Constructor
    def __init__(self):
        self.con = psycopg2.connect(config.db_string)
        self.cur = self.con.cursor()
        self.create_data_table()

        #After DB is created, set a timeout for inserts
        self.cur.execute("SET statement_timeout = 5")

    def create_data_table(self):
        if config.testing == True:
            self.cur.execute("""DROP TABLE voltronic_log""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS voltronic_log
                            (
                            timestamp TIMESTAMP PRIMARY KEY,
                            grid_voltage DECIMAL,
                            grid_frequency DECIMAL,
                            inverter_voltage DECIMAL,
                            inverter_frequency DECIMAL,
                            inverter_apparent_output DECIMAL,
                            inverter_active_power DECIMAL,
                            inverter_load DECIMAL,
                            bus_voltage DECIMAL,
                            battery_voltage DECIMAL,
                            charge_current DECIMAL,
                            battery_capacity DECIMAL,
                            inverter_temperature DECIMAL,
                            pv_input_current DECIMAL,
                            pv_input_voltage DECIMAL,
                            battery_voltage_scc DECIMAL,
                            discharge_current DECIMAL,
                            inverter_status TEXT,
                            battery_voltage_offset_fan DECIMAL,
                            eeprom_version TEXT,
                            pv_in_power DECIMAL,
                            device_status TEXT,
                            mode TEXT,
                            grid_rating_voltage DECIMAL,
                            grid_rating_current DECIMAL,
                            ac_output_rating_voltage DECIMAL,
                            ac_output_rating_frequency DECIMAL,
                            ac_output_rating_current DECIMAL,
                            ac_output_rating_apparent_power DECIMAL,
                            ac_output_rating_active_power DECIMAL,
                            battery_rating_voltage DECIMAL,
                            battery_recharge_voltage DECIMAL,
                            battery_under_voltage DECIMAL,
                            battery_bulk_voltage DECIMAL,
                            Battery_float_voltage DECIMAL,
                            battery_type TEXT,
                            current_max_ac_charging_current DECIMAL,
                            current_max_charging_current DECIMAL,
                            input_voltage_range TEXT,
                            output_source_priority TEXT,
                            charger_source_priority TEXT,
                            parallel_max_num DECIMAL,
                            machine_type TEXT,
                            topology TEXT,
                            output_mode TEXT,
                            battery_redischarge_voltage DECIMAL,
                            pv_ok_condition_for_parallel TEXT,
                            pv_power_balance TEXT,
                            unknown TEXT
                            )
                            """)

    def insert(self, data_list):
        try:
            self.cur.execute("""INSERT INTO voltronic_log VALUES(current_timestamp,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                data_list)
            # Commit changes    
            self.con.commit()
        except:
            # Write a log
            log_warning("Failed to insert row!")
            # Can try infinitely without crashing
            try:
                log_warning("Reconnecting...")
                self.con.close()
                self.con = psycopg2.connect(config.db_string)
                self.cur = self.con.cursor()
                self.cur.execute("SET statement_timeout = 5")
            except:
                log_warning("Failed to reconnect to DB!")
                pass

    def close(self):
        # Disconnect from the DB
        self.con.close()

############################################################
# MQTT class 
############################################################
class Mqtt:
    #Constructor
    def __init__(self):
        # Create an MQTT client instance
        self.client = mqtt_c.Client()
        # Set the username and password
        self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
        # Set callback for message
        self.client.on_message = self.on_message
        # Connect to the MQTT broker
        self.client.connect(config.mqtt_broker)
        # Subscribe to topic for commands from HomeAssistant
        self.client.subscribe(config.mqtt_subscribe_topic)
        # Retry counter
        self.retry_count = 0

    def setupDiscovery(self):
        # Setup Sensors...
        with open('mqtt_discovery.json') as sensors_file:
            sensors_config = json.load(sensors_file)

        for sensor in sensors_config:
            sensor["device"]["name"] = config.inverter_make + " " + config.inverter_model
            sensor["device"]["identifiers"] = config.inverter_serial_number
            sensor["device"]["manufacturer"] = config.inverter_make
            sensor["device"]["model"] = config.inverter_model
            sensor["state_topic"] = config.mqtt_publish_topic
            config_topic = "homeassistant/sensor/" + sensor["unique_id"] + "/config"
            self.client.publish(config_topic, json.dumps(sensor))

    def publish(self, data_dict):
        try:
            # Convert to JSON
            json_data = json.dumps(data_dict)
            # Publish the message to the topic, refresh connection and retry on fail
            if self.client.publish(config.mqtt_publish_topic, json_data)[0] != 0:
                raise Exception("Failed to publish")
        except:
            # Try to restablish connection
            log_warning("Could not publish")
            try:
                self.client.disconnect()
                log_warning("Reconnecting...")
                self.client.connect(config.mqtt_broker)
                log_warning("Reconnected! Resubscribing...")
                self.client.subscribe(config.mqtt_subscribe_topic)
                log_warning("Resubscribed!")
                self.retry_count = 0
            except:
                self.retry_count += 1
                log_warning("Failed to reconnect to broker attempt: " + str(self.retry_count))
                pass

    def listen(self):
        # Check topic
        self.client.loop_read()

    def on_message(self, client, userdata, msg):
        # log whatever is sent
        try:
            payload = str(msg.payload.decode("UTF-8"))
            log_warning(payload)
            command_response = execute_command(payload)
            log_warning(str(command_response))
        except:
            log_warning("Could not update settings!")
            
    def close(self):
        # Disconnect from the MQTT broker
        self.client.disconnect()

############################################################
# Device general status enquiry
############################################################
class Qpigs:
    #Constructor
    def __init__(self, qpigs):
        #instance variables
        self.grid_voltage = qpigs[0]
        self.grid_frequency = qpigs[1]
        self.inverter_voltage = qpigs[2]
        self.inverter_frequency = qpigs[3]
        self.inverter_apparent_output = qpigs[4]
        self.inverter_active_power = qpigs[5]
        self.inverter_load = qpigs[6]
        self.bus_voltage = qpigs[7]
        self.battery_voltage = qpigs[8]
        self.charge_current = qpigs[9]
        self.battery_capacity = qpigs[10]
        self.inverter_temperature = qpigs[11]
        self.pv_input_current = qpigs[12]
        self.pv_input_voltage = qpigs[13]
        self.battery_voltage_scc = qpigs[14]
        self.discharge_current = qpigs[15]
        self.inverter_status = qpigs[16]
        self.battery_voltage_offset_fan = qpigs[17]
        self.eeprom_version= qpigs[18]
        self.pv_in_power = qpigs[19]
        self.device_status = qpigs[20]

############################################################
# Device serial number enquiry
############################################################
class Qid:
    #Constructor
    def __init__(self, qid):
        #instance variables
        self.serial_number = qid[0]

############################################################
# Device mode enquiry
############################################################
class Qmod:
    #Constructor
    def __init__(self, qmod):
        #instance variables
        self.mode = qmod[0]

############################################################
# Device rating information enquiry
############################################################
class Qpiri:
    #Constructor
    def __init__(self, qpiri):
        #instance variables
        self.grid_rating_voltage = qpiri[0]
        self.grid_rating_current = qpiri[1]
        self.ac_output_rating_voltage = qpiri[2]
        self.ac_output_rating_frequency = qpiri[3]
        self.ac_output_rating_current = qpiri[4]
        self.ac_output_rating_apparent_power = qpiri[5]
        self.ac_output_rating_active_power = qpiri[6]
        self.battery_rating_voltage = qpiri[7]
        self.battery_recharge_voltage = qpiri[8]
        self.battery_under_voltage = qpiri[9]
        self.battery_bulk_voltage = qpiri[10]
        self.battery_float_voltage = qpiri[11]
        self.battery_type = qpiri[12]
        self.current_max_ac_charging_current = qpiri[13]
        self.current_max_charging_current = qpiri[14]
        self.input_voltage_range = qpiri[15]
        self.output_source_priority = qpiri[16]
        self.charger_source_priority = qpiri[17]
        self.parallel_max_num = qpiri[18]
        self.machine_type = qpiri[19]
        self.topology = qpiri[20]
        self.output_mode = qpiri[21]
        self.battery_redischarge_voltage = qpiri[22]
        self.pv_ok_condition_for_parallel = qpiri[23]
        self.pv_power_balance = qpiri[24]
        self.unknown = qpiri[25]

############################################################
# Timeout class
############################################################
class Timeout:
    def __init__(self, seconds=1, error_message='Timeout!'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        log_warning(self.error_message)
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)