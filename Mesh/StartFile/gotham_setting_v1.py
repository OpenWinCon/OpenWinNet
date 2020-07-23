import random as np
import netifaces as ni
import os
import sys
import subprocess
import time

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
   print("-----------check_mesh_beacon start----------")
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

def get_compatible_ip(ipSetting):
   print("----------get compatible ip----------")
   #ni.ifaddresses('br0')
   #ip = ni.ifaddresses('br0')[2][0]['addr']
   #ip_array = ip.split('.')

   ip_array = ipSetting.split('.')

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
   print("----------searching_beacon----------")
   os.system("hciconfig hci- down")
   time.sleep(2)
   os.system("hciconfig hci- up")
   time.sleep(2)
   print(">>>>>>>>>>beacon scanning<<<<<<<<<<")
   task = subprocess.Popen("timeout 3s /etc/gotham/beacon_scan_mesh.sh", shell=True, stdout=subprocess.PIPE)
   time.sleep(2)
   task = subprocess.Popen("timeout 10s /etc/gotham/beacon_scan_mesh.sh", shell=True, stdout=subprocess.PIPE)
   data = task.stdout.read()
   scan_beacon = data.split('\n')
   for i in scan_beacon:
      if(check_mesh_beacon(i)==True):
         return get_information_from_line(i)
   returnValue = ["False", "False"]
   return returnValue

def setting_beacon(version, ip, ssid, channel):
   print("----------setting_beacon & command----------")
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
   return ssid + " " + channel

def first_random_setting(ipSetting):
   version = "00"
   mainIP = get_compatible_ip(ipSetting)
   ssid='{0:0>2}'.format(hex(np.randrange(0,256))[2:]).upper() + " " + '{0:0>2}'.format(hex(np.randrange(0,256))[2:]).upper()
   channel='{0:0>2}'.format(np.randrange(1,12))

   setting_value =[version, mainIP, ssid, channel]
   return setting_value

def setting_network(isGWserver):
   print("----------setting_network----------")
   
   os.system("service network-manager stop")
   time.sleep(10)
   os.system("service network-manager start")
   time.sleep(10)
   os.system("service network-manager stop")
   time.sleep(10)
   os.system("modprobe batman-adv")
   time.sleep(5)
   if(isGWserver!="F"):
      setting_backhole()

def setting_batman(ifname, isGWserver, ssid, channel):
   print("----------setting_batman----------")
   channel_str = str(channel)
   bat_number = ifname[4]
   os.system("ifconfig " + ifname + " down")
   os.system("iwconfig " + ifname + " mode ad-hoc essid " + ssid + " channel " + channel_str)
   print("iwconfig " + ifname + " mode ad-hoc essid " + ssid + " channel " + channel_str)
   os.system("ifconfig " + ifname + " up")
   time.sleep(2)
   os.system("batctl -m bat" + bat_number +" if add " + ifname)
   print("batctl -m bat" + bat_number +" if add " + ifname)
   os.system("ifconfig " + ifname + " mtu 1527")
   os.system("cat /sys/class/net/" + ifname + "/batman_adv/iface_status")
   os.system("ifconfig bat" + bat_number +" up")
                                
   time.sleep(5)
                                    
   if(isGWserver == "F"):
      os.system("batctl -m bat" + bat_number +" gw client")
   else:
      os.system("batctl -m bat" + bat_number +" gw server")

def setting_OVS(isGWserver, ipSetting):
   print("----------setting_OVS----------")
   os.system("ovs-vsctl del-br br0")
   os.system("ovs-vsctl add-br br0")
   os.system("ifconfig br0 up")

   if(isGWserver != "F"):
      os.system("ovs-vsctl add-port br0 " + isGWserver)
      os.system("ifconfig " + isGWserver + " 0")

   if(ipSetting == "F"):
      print("----------get ip from DHCP server----------")
      os.system("dhclient br0")
      time.sleep(10)
   else:
      os.system("ifconfig br0 " + ipSetting)

def add_OVS_port(ifCount, ifname):
   print("----------OVS_addPort----------")
   for i in range(0, ifCount):
      os.system("ovs-vsctl add-port br0 bat" + ifname[i][4]);
      print(str(i) + " " + ifname[i])

def setting_AP():
   task = subprocess.Popen("hostapd -dd /etc/hostapd/hostapd.conf", shell=True, stdout=subprocess.PIPE)
   time.sleep(5)

def setting_GOTHAM_main_main():
   os.system("java -jar /etc/gotham/GOTHAM_hazel.jar wlan0 1 192.168.1.10")

def setting_GOTHAM_main_subordinate():
   os.system("java -jar /etc/gotham/GOTHAM_hazel.jar wlan0 2 192.168.1.10")

def setting_backhole():
   os.system("ifconfig wlan1 up")
   time.sleep(2)
   os.system("iw dev wlan1 connect FUN5G-AP#2")
#  os.system("dhclient wlan1")
#  time.sleep(5)

#[T or F] : Beacon setting or Default setting
#[interface name(eth0) or F] : GW server or Not
#[T or F] : AP mode
#[M or S or F] : GOTHAM_main start
#[interface name(wlan0)] : mesh interface name
#[F or IP(193.168.1.10)] : DHCP or Static IP
#[interface name(wlan1) or F] : second mesh inteface(defualt control plane)
if __name__ == "__main__":
   argvCount = len(sys.argv)
   if(argvCount != 8):
      print("----------check the parameter----------")
      sys.exit(0)
   startWithBeacon = sys.argv[1]
   isGWserver = sys.argv[2]
   isAP = sys.argv[3]
   isGOTHAM = sys.argv[4]
   interfaceName = sys.argv[5]
   ipSetting = sys.argv[6]
   isSecondMesh = sys.argv[7]

   setting_network(isGWserver)
   if(startWithBeacon == "T"):
      print("----------start GOTHAM with beacon----------")
      beaconExisting=searching_beacon()
      print(beaconExisting)

      if(beaconExisting[0] == "False"):
         print("beacon is not detecting")
         ipSetting = "192.168.1.10"
         first_setting = first_random_setting(ipSetting)
      
      else:
         print("beacon detecting")
         first_setting = beaconExisting

      batman_info = setting_beacon(first_setting[0], first_setting[1], first_setting[2], first_setting[3])
      batman_info_split = batman_info.split(' ')
      conv_ssid = batman_info_split[0]+batman_info_split[1]

      setting_batman(interfaceName, isGWserver, conv_ssid, batman_info_split[2])

   else:
      print("----------start GOTHAM without beacon----------")
      setting_batman(interfaceName, isGWserver, "gotham_public", 1)

   setting_OVS(isGWserver, ipSetting)
   

   if(isSecondMesh != "F"):
      setting_batman(isSecondMesh, "F", "gotham_private", 9)
      ifname_array=[interfaceName, isSecondMesh]
      add_OVS_port(2, ifname_array)
   else:
      ifname_array=[interfaceName, "NULL"]
      add_OVS_port(1, ifname_array)

   if(isAP == "T"):
      print("----------start AP mode----------")
      setting_AP()

   if(isGOTHAM =="M"):
      print("----------start GOTHAM main----------")
      setting_GOTHAM_main_main()
   elif(isGOTHAM =="S"):
      setting_GOTHAM_main_subordinate()
