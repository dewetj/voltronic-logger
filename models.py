import psycopg2
import paho.mqtt.client as mqtt_c
import json
import config

############################################################
# Postgres DB class
############################################################
class Elephant_db:
    #Constructor
    def __init__(self):
        self.con = psycopg2.connect(config.db_string)
        self.cur = self.con.cursor()
        self.create_data_table()

    def create_data_table(self):
        #self.cur.execute("""DROP TABLE voltronic_log""")
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
                            mode TEXT
                            )
                            """)

    def insert(self, data_list):
        try:
            self.cur.execute("""INSERT INTO voltronic_log VALUES(current_timestamp,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                data_list)
        except:
            # Write a log
            print("Failed to insert row")
            # Can try infinitely without crashing
            try:
                print("Reconnecting...")
                self.con.close()
                self.con = psycopg2.connect(config.db_string)
                self.cur = self.con.cursor()
            except:
                print("Failed to reconnect to DB!")
                pass

        # Commit changes    
        self.con.commit()

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
        # Connect to the MQTT broker
        self.client.connect(config.mqtt_broker)

    def publish(self, data_dict):
        try:
            # Convert to JSON
            json_data = json.dumps(data_dict)
            # Publish the message to the topic, refresh connection and retry on fail
            if self.client.publish(config.mqtt_topic, json_data)[0] != 0:
                raise Exception("Failed to publish")
        except:
            # Try to restablish connection
            print("Could not publish")
            try:
                self.client.disconnect()
                self.client.connect(config.mqtt_broker)
                print("Reconnecting...")
            except:
                print("Failed to reconnect to broker!")
                pass

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
        self.unk1 = qpigs[17]
        self.unk2 = qpigs[18]
        self.unk3 = qpigs[19]
        self.unk4 = qpigs[20]

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

