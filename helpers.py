import crcmod
import time
import config
import os
from datetime import datetime

xmodem_crc_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

#Request Structures
qpigs_structure = ['grid_voltage', 'grid_frequency', 'inverter_voltage', 'inverter_frequency', 'inverter_apparent_output', 'inverter_active_power', 'inverter_load', 'bus_voltage', 'battery_voltage','charge_current',
                    'battery_capacity','inverter_temperature','pv_input_current','pv_input_voltage','battery_voltage_scc','discharge_current','inverter_status','battery_voltage_offset_fan','eeprom_version','pv_in_power','device_status']
dummy_qpigs = ['240.0', '50.0', '240.0', '50.0', '0368', '0278', '007', '346', '49.70', '050', '096', '0042', '00.0', '000.0', '00.00', '00000', '00010000', '00', '00', '00000', '010']

qid_structure = ['serial_number']
dummy_qid = ['12345678901234zx9fxzr']

qmod_structure = ['mode']
dummy_qmod = ['L']

qpiri_structure = ['grid_rating_voltage', 'grid_rating_current', 'ac_output_rating_voltage', 'ac_output_rating_frequency', 'ac_output_rating_current', 'ac_output_rating_apparent_power', 'ac_output_rating_active_power', 'battery_rating_voltage',
                    'battery_recharge_voltage', 'battery_under_voltage', 'battery_bulk_voltage', 'Battery_float_voltage', 'battery_type', 'current_max_ac_charging_current', 'current_max_charging_current', 'input_voltage_range',
                     'output_source_priority', 'charger_source_priority', 'parallel_max_num', 'machine_type', 'topology', 'output_mode', 'battery_redischarge_voltage', 'pv_ok_condition_for_parallel', 'pv_power_balance', 'unknown']
dummy_qpiri = ['230.0', '21.7', '230.0', '50.0', '21.7', '5000', '5000', '48.0', '48.0', '45.0', '53.2', '53.2', '3', '050', '000', '1', '0', '2', '9', '00', '0', '0', '51.0', '0', '1', '000']

pcp_structure = ['response']
dummy_pcp = ['ACK']

def execute_command(command):
    log_info("Executing " + command + "...")
    if command == 'QPIGS':
        nbytes = 110
        return_list = dummy_qpigs
    elif command == 'QID':
        nbytes = 18
        return_list = dummy_qid
    elif command == 'QMOD':
        nbytes = 5
        return_list = dummy_qmod
    elif command == 'QPIRI':
        nbytes = 102
        return_list = dummy_qpiri
    elif command[0:3] == 'PCP':
        nbytes = 5
        return_list = dummy_pcp
    elif command[0:3] == 'POP':
        nbytes = 5
        return_list = dummy_pcp
    else:
        return ['']

    #TESTING!!!!!
    if config.testing == True:
        return return_list

    # Encode command and calculate CRC
    command_bytes = command.encode('ISO-8859-1')
    crc_val = xmodem_crc_func(command_bytes)
    crc_bytes = crc_val.to_bytes(2, byteorder='big')
    bytes_command = command_bytes + crc_bytes + b'\r'

    try:
        fd = open('/dev/hidraw0', 'rb+') #Open file to read and write in bytes (rb+)
        fd.write(bytes_command)

        #Wait a second in case there is a delayed response...
        time.sleep(1)
        data_in_bytes = fd.read(nbytes)
        fd.close()

        data_in_string = data_in_bytes.decode('ISO-8859-1')
        data_as_list = data_in_string.split("//")
        return_list = data_as_list[0][1:].split(" ")
        
    except Exception as e:
        log_warning("File error:")
        log_warning(str(e))
        # Thow the exception again after logging so the service can restart
        raise Exception("See log.txt!!!")

    return return_list

def map_mode(qmod):
    modes = {"P":"Power On","S":"Standby","L":"Line","B":"Battery","F":"Fault","H":"Power saving"}
    return modes[qmod[0]]
        
def map_datatypes(data_list):
    out_data = []
    string_indices = {16, 18, 34, 37, 38, 39, 41, 42, 43, 45, 46}
    
    for i, val in enumerate(data_list):
        if i == 20:
            # Clean device status as it sometimes has CRC values appended
            out_data.append(val[0:3])
        elif i == 21:
            # Clean mode as it can have shitty data in for some weird reason.
            char = val[0:1]
            out_data.append(char if char in ['P','S','L','B','F','H'] else ' ')
        elif i == 47:
            out_data.append(val[0:3])
        elif i in string_indices:
            out_data.append(val)
        else:
            out_data.append(float(val))
            
    return out_data

def create_dict(data_list):
    data_keys = qpigs_structure + qmod_structure + qpiri_structure
    data_dict = dict(zip(data_keys, data_list))
    return data_dict

def log_warning(message):
    if config.log_warning == True:
        sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
        with open(config.log_location, 'a') as f:
            f.write(sttime + message)
            f.write('\n')

def log_info(message):
    if config.log_info == True:
        sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
        with open(config.log_location, 'a') as f:
            f.write(sttime + message)
            f.write('\n')

def backup_log():
    try:
        sttime = datetime.now().strftime('_%Y%m%d_%H%M%S.txt')
        os.rename(config.log_location, config.log_location.replace('.txt',sttime))
        log_warning("Previous log backed up!")
    except FileNotFoundError:
        log_warning("No previous log found!")
    except Exception as e:
        log_warning(f"Failed to backup log: {e}")
