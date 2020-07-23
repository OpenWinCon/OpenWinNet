import random as np
import netifaces as ni
import os
import sys
import subprocess

def check_MAJOR(major):
        if(major == "3840"):
                return True
        else:
                return False

def check_MINOR(minor):
        if(minor == "3840"):
                return True
        else:
                return False

def check_POWER(power):
        if(power == "-56"):
                return True
        else:
                return False

def check_mesh_beacon(scan_beacon):
        print("--------check_mesh_beacon start--------")
        split_data = scan_beacon.split(' ')
        for i in split_data:
                checking_data=i.split(':')
                if(checking_data[0] == "MAJOR"):
                        if(check_MAJOR(checking_data[1])==False):
                                return False
                elif(checking_data[0] == "MINOR"):
                        if(check_MINOR(checking_data[1])==False):
                                return False
                elif(checking_data[0] == "POWER"):
                        if(check_POWER(checking_data[1])==False):
                                return False
                elif(checking_data[0] != "UUID"):
                        return False

        print("chcking mesh : True")
        return True

def get_ip():
        print("--------get my ip---------")
        ni.ifaddresses('eth0')
        ip = ni.ifaddresses('eth0')[2][0]['addr']
        ip_array = ip.split('.')

        ip_dec = [0, 0, 0, 0]
        ip_hex = ['0', '0', '0', '0']
        for i in range(0, 4):
                ip_dec[i] = int(ip_array[i])
                ip_hex[i] = str(hex(ip_dec[i])[2:]).upper()

        beacon_compatible_IP = ip_hex[0] + " " + ip_hex[1] + " " + ip_hex[2] + " " + ip_hex[3]
        return beacon_compatible_IP

def get_information_from_line(line):
        split_data = line.split(' ')
        for i in split_data:
                checking_data=i.split(':')
                if(checking_data[0] == "UUID"):
                        uuid = checking_data[1]
                        break;
        version = uuid[0:2]
        mainIP = uuid[2:4] + " " + uuid[4:6] + " " + uuid[6:8] + " "+ uuid[8:10]
        ssid = uuid[10:12] + " " + uuid[12:14]
        channel = uuid[14:16]
        returnArray = [version, mainIP, ssid, channel]
        return returnArray

def searching_beacon():
        print("--------searching_beacon--------")
        task = subprocess.Popen("timeout 5s ./beacon_scan_mesh.sh", shell=True, stdout=subprocess.PIPE)
        data = task.stdout.read()
        scan_beacon = data.split('\n')
        for i in scan_beacon:
                if(check_mesh_beacon(i)==True):
                        return get_information_from_line(i)
        returnValue = ["False", "False"]
        return returnValue

def setting_beacon(version, ip, ssid, channel):
        print("--------setting_beacon & command--------")
        beacon_header = "1E 02 01 1A 1A FF "
        beacon_company = "00 FF "
        beacon_middle = "02 15 "

        mesh_version = version + " "
        mesh_mainIP = ip  + " "
        mesh_ssid=ssid + " "
        mesh_channel=channel + " "
        mesh_blank="00 00 00 00 00 00 00 00 "
        beacon_uuid = mesh_version + mesh_mainIP + mesh_ssid + mesh_channel + mesh_blank
        beacon_tail = "0F 00 0F 00 C8 00"
        print("version : %s" %mesh_version)
        print("mainIP : %s" %mesh_mainIP)
        print("ssid : %s" %mesh_ssid)
        print("channel : %s" %mesh_channel)

        #hci_name = sys.argv[1] + " "
        command = "sudo hcitool -i "
        command += "hci- "
        command += "cmd 0x08 0x008 " + beacon_header + beacon_company + beacon_middle + beacon_uuid + beacon_tail
        #print(command)
        os.system(command)

def first_random_setting():
        version = "00"
        mainIP = get_ip()
        ssid='{0:0>2}'.format(hex(np.randrange(0,256))[2:]).upper() + " " + '{0:0>2}'.format(hex(np.randrange(0,256))[2:]).upper()
        channel='{0:0>2}'.format(np.randrange(1,12))

        setting_value =[version, mainIP, ssid, channel]
        return setting_value

if __name__ == "__main__":
        input_from_out = sys.argv[1]
        if(input_from_out == "F"):
                beaconExisting=searching_beacon()
                print(beaconExisting)
                if(beaconExisting[0] == "False"):
                        print("beacon is not detecting")
                        first_setting = first_random_setting()
                else:
                        print("beacon detecting")
                        first_setting = beaconExisting
                setting_beacon(first_setting[0], first_setting[1], first_setting[2], first_setting[3])
        else:
                print("nothing”)
