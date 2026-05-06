import crcmod
import time
import config
import os
from datetime import datetime

xmodem_crc_func = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

#Request Structures
qpigs_structure = [
    'grid_voltage',                # Field 1
    'grid_frequency',              # Field 2
    'inverter_voltage',            # Field 3
    'inverter_frequency',          # Field 4
    'inverter_apparent_output',    # Field 5
    'inverter_active_power',       # Field 6
    'inverter_load',               # Field 7
    'bus_voltage',                 # Field 8
    'battery_voltage',             # Field 9
    'charge_current',              # Field 10
    'battery_capacity',            # Field 11
    'inverter_temperature',        # Field 12
    'pv_input_current',            # Field 13
    'pv_input_voltage',            # Field 14
    'battery_voltage_scc',         # Field 15
    'discharge_current',           # Field 16
    'inverter_status',             # Field 17
    'battery_voltage_offset_fan',  # Field 18
    'eeprom_version',              # Field 19
    'pv_in_power',                 # Field 20
    'device_status'                # Field 21
]

dummy_qpigs = [
    '240.0',    # Field 1
    '50.0',     # Field 2
    '240.0',    # Field 3
    '50.0',     # Field 4
    '0368',     # Field 5
    '0278',     # Field 6
    '007',      # Field 7
    '346',      # Field 8
    '49.70',    # Field 9
    '050',      # Field 10
    '096',      # Field 11
    '0042',     # Field 12
    '00.0',     # Field 13
    '000.0',    # Field 14
    '00.00',    # Field 15
    '00000',    # Field 16
    '00010000', # Field 17
    '00',       # Field 18
    '00',       # Field 19
    '00000',    # Field 20
    '010'       # Field 21
]

qid_structure = [
    'serial_number'  # Field 1
]

dummy_qid = [
    '12345678901234zx9fxzr'  # Field 1
]

qmod_structure = [
    'mode'  # Field 1
]

dummy_qmod = [
    'L'  # Field 1
]

qpiri_structure = [
    'grid_rating_voltage',               # Field 1
    'grid_rating_current',               # Field 2
    'ac_output_rating_voltage',          # Field 3
    'ac_output_rating_frequency',        # Field 4
    'ac_output_rating_current',          # Field 5
    'ac_output_rating_apparent_power',   # Field 6
    'ac_output_rating_active_power',     # Field 7
    'battery_rating_voltage',            # Field 8
    'battery_recharge_voltage',          # Field 9
    'battery_under_voltage',             # Field 10
    'battery_bulk_voltage',              # Field 11
    'battery_float_voltage',             # Field 12
    'battery_type',                      # Field 13
    'current_max_ac_charging_current',   # Field 14
    'current_max_charging_current',      # Field 15
    'input_voltage_range',               # Field 16
    'output_source_priority',            # Field 17
    'charger_source_priority',           # Field 18
    'parallel_max_num',                  # Field 19
    'machine_type',                      # Field 20
    'topology',                          # Field 21
    'output_mode',                       # Field 22
    'battery_redischarge_voltage',       # Field 23
    'pv_ok_condition_for_parallel',      # Field 24
    'pv_power_balance',                  # Field 25
    'unknown'                            # Field 26
]

dummy_qpiri = [
    '230.0', # Field 1
    '21.7',  # Field 2
    '230.0', # Field 3
    '50.0',  # Field 4
    '21.7',  # Field 5
    '5000',  # Field 6
    '5000',  # Field 7
    '48.0',  # Field 8
    '48.0',  # Field 9
    '45.0',  # Field 10
    '53.2',  # Field 11
    '53.2',  # Field 12
    '3',     # Field 13
    '050',   # Field 14
    '000',   # Field 15
    '1',     # Field 16
    '0',     # Field 17
    '2',     # Field 18
    '9',     # Field 19
    '00',    # Field 20
    '0',     # Field 21
    '0',     # Field 22
    '51.0',  # Field 23
    '0',     # Field 24
    '1',     # Field 25
    '000'    # Field 26
]

qpiws_structure = [
    'inverter_fault',              # Bit 1
    'bus_over_voltage',            # Bit 2
    'bus_under_voltage',           # Bit 3
    'bus_soft_start_fail',         # Bit 4
    'line_fail',                   # Bit 5
    'opv_short_(output_short)',    # Bit 6
    'inverter_voltage_low',        # Bit 7
    'inverter_voltage_high',       # Bit 8
    'over_temperature',            # Bit 9
    'fan_locked',                  # Bit 10
    'inverter_over_temperature',   # Bit 11
    'battery_voltage_high',        # Bit 12
    'overload',                    # Bit 13
    'charge_pump_fail',            # Bit 14
    'solar_charger_loss',          # Bit 15
    'parallel_relay_fail',         # Bit 16
    'output_voltage_critical',     # Bit 17
    'power_limit',                 # Bit 18
    'bypass_forbidden',            # Bit 19
    'battery_low',                 # Bit 20
    'charge_high_(overcharge)',    # Bit 21
    'over_current',                # Bit 22
    'over_70%_load',               # Bit 23
    'pv_voltage_high',             # Bit 24
    'mppt_over_temperature',       # Bit 25
    'mppt_overload',               # Bit 26
    'battery_disconnected',        # Bit 27
    'battery_under_voltage',       # Bit 28
    'fan_2_locked',                # Bit 29
    'solar_charger_firmware_fail', # Bit 30
    'reserved'                     # Bit 31
]
dummy_qpiws = [
    '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', # Bits 1-10
    '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', # Bits 11-20
    '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', # Bits 21-30
    '0'                                               # Bit 31
]

pcp_structure = ['response']
dummy_pcp = ['ACK']

def execute_command(command):
    log_info("Executing " + command + "...")
    
    command_map = {
        'QPIGS': (110, dummy_qpigs),
        'QID': (18, dummy_qid),
        'QMOD': (5, dummy_qmod),
        'QPIRI': (102, dummy_qpiri),
        'QPIWS': (36, dummy_qpiws)
    }

    if command in command_map:
        nbytes, return_list = command_map[command]
    elif command[0:3] in ('PCP', 'POP'):
        nbytes, return_list = (5, dummy_pcp)
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
    data_keys = qpigs_structure + qmod_structure + qpiri_structure + qpiws_structure
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
