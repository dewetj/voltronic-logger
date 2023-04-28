import crcmod
import datetime
import config
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

def calc_crc(comando):
    global crc
    crc = hex(xmodem_crc_func(comando))
    return crc

def execute_command(command):
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
    else:
        return ['']

    #TESTING!!!!!
    if config.testing == True:
        return return_list

    calc_crc(command.encode('utf-8'))

    crc1=crc[0:4]
    crc2=crc[0:2]+crc[4:6]

    crc1=int(crc1, base=16)
    crc2=int(crc2, base=16)

    string_command = command+chr(crc1)+chr(crc2)+'\r'
    bytes_command = string_command.encode('ISO-8859-1')

    try:
        fd = open('/dev/hidraw0', 'rb+') #Open file to read and write in bytes (rb+)
        fd.flush()
        fd.write(bytes_command)
        data_in_bytes = fd.read(nbytes)
        fd.close()           
        data_in_string = data_in_bytes.decode('ISO-8859-1')
        data_as_list = data_in_string.split("//")
        return_list = data_as_list[0][1:].split(" ")
    except Exception as e:
        log_warning("Failed to write " + command + " with exception:")
        log_warning(str(e))
        #Hard crash so service can restart and usb remounts
        raise Exception("Forced crash!")
    
    return return_list

def map_mode(qmod):
    modes = {"P":"Power On","S":"Standby","L":"Line","B":"Battery","F":"Fault","H":"Power saving"}
    return modes[qmod[0]]
        
def map_datatypes(data_list):
    out_data = list()
    #QPIGS
    out_data.append(float(data_list[0]))
    out_data.append(float(data_list[1]))
    out_data.append(float(data_list[2]))
    out_data.append(float(data_list[3]))
    out_data.append(float(data_list[4]))
    out_data.append(float(data_list[5]))
    out_data.append(float(data_list[6]))
    out_data.append(float(data_list[7]))
    out_data.append(float(data_list[8]))
    out_data.append(float(data_list[9]))
    out_data.append(float(data_list[10]))
    out_data.append(float(data_list[11]))
    out_data.append(float(data_list[12]))
    out_data.append(float(data_list[13]))
    out_data.append(float(data_list[14]))
    out_data.append(float(data_list[15]))
    out_data.append(data_list[16])
    out_data.append(float(data_list[17]))
    out_data.append(data_list[18])
    out_data.append(float(data_list[19]))
    #Clean device status as it sometimes has CRC values appended
    out_data.append(data_list[20][0:3])
    #Clean mode as it can have shitty data in for some weird reason.
    if data_list[21][0:1] not in ['P','S','L','B','F','H']:
        out_data.append(' ')
    else:
        out_data.append(data_list[21][0:1])
    #QPIRI
    out_data.append(float(data_list[22]))
    out_data.append(float(data_list[23]))
    out_data.append(float(data_list[24]))
    out_data.append(float(data_list[25]))
    out_data.append(float(data_list[26]))
    out_data.append(float(data_list[27]))
    out_data.append(float(data_list[28]))
    out_data.append(float(data_list[29]))
    out_data.append(float(data_list[30]))
    out_data.append(float(data_list[31]))
    out_data.append(float(data_list[32]))
    out_data.append(float(data_list[33]))
    out_data.append(data_list[34])
    out_data.append(float(data_list[35]))
    out_data.append(float(data_list[36]))
    out_data.append(data_list[37])
    out_data.append(data_list[38])
    out_data.append(data_list[39])
    out_data.append(float(data_list[40]))
    out_data.append(data_list[41])
    out_data.append(data_list[42])
    out_data.append(data_list[43])
    out_data.append(float(data_list[44]))
    out_data.append(data_list[45])
    out_data.append(data_list[46])
    out_data.append(data_list[47][0:3])
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