import serial
import sys
from guizero import *
import glob
import time


def get_serial_ports_list():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


ports = get_serial_ports_list()
if not ports:
    ports = ['null']

print(ports)
ser = serial.Serial()
ser.baudrate = 19200

def open_port():
    ser.port = combo.get()
    ser.open()
    if ser.is_open:
        Picture(app, image='conn.png', grid=[0, 4])
        print('port is connected')
        #time.sleep(1)
        request_state()
    else:
        Picture(app, image='discon.png', grid=[0, 4])
    return ser


def close_port(ser):
    ser.close()
    if ser.is_open:
        Picture(app, image='conn.png', grid=[0, 4])
    else:
        Picture(app, image='discon.png', grid=[0, 4])
        print('port is disconnected')
    for i in range(0, 8):
        Picture(app, image='discon.png', grid=[i + 2, 4])


def send_command(relay, param):
    request = '{}{}'.format(relay, param)
    print(request)
    print(request.encode(encoding='UTF-8'))
    ser.write(request.encode(encoding='UTF-8'))


def switch_relay_on(relay):
    send_command(relay, '1')
    Picture(app, image='conn.png', grid=[relay+2, 4])


def switch_relay_off(relay):
    send_command(relay, '0')
    Picture(app, image='discon.png', grid=[relay+2, 4])


def request_state():
    request = '{}{}'.format("!", "!")
    ser.write(request.encode(encoding='UTF-8'))
    pins_state_str = ser.readline().decode("utf-8")
    #print(pins_state_str)
    #pins = list(pins_state_str)
    print(pins_state_str)
    for i, l in enumerate(pins_state_str):
        if l == '0':
            Picture(app, image='discon.png', grid=[(i + 2), 4])
            print("printing icon discon on %s position" % (i+2))
            i += 1
        elif l == '1':
            Picture(app, image='conn.png', grid=[(i + 2), 4])
            i += 1


app = App(title="SGRO power management",layout="grid", width=370, height=450)
text = Text(app, text="Select Port:", grid=[0,0])
combo = Combo(app, options=tuple(ports), grid=[0,1])
connect_btn = PushButton(app, text='Connect', command=open_port, grid=[0,2])
disconnect_btn = PushButton(app, text='Disconnect', command=lambda: close_port(ser), grid=[0,3])
#request_stat = PushButton(app, text = 'Get pins', command=lambda: request_state(), grid=[1,0])
Picture(app, image='discon.png', grid=[0, 4])
Text(app, text=" ", grid=[1,0])


# for r in range(0,8):
#     relay_label = Text(app, text="Relay %s" % (r+1), grid=[r+2,0])
#     relay_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(r), grid=[r+2,2])
#     relay_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(r), grid=[r+2,3])

# for i in range(0,8):
#     Picture(app, image='discon.png', grid=[i+2, 4])


#Relay #1
relay1_label = Text(app, text="Relay 1", grid=[2,0])
relay1_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(0), grid=[2,2])
relay1_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(0), grid=[2,3])

#Relay #2
relay2_label = Text(app, text="Relay 2", grid=[3,0])
relay2_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(1), grid=[3,2])
relay2_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(1), grid=[3,3])

#Relay #1
relay3_label = Text(app, text="Relay 3", grid=[4,0])
relay3_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(2), grid=[4,2])
relay3_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(2), grid=[4,3])

#Relay #1
relay4_label = Text(app, text="Relay 4", grid=[5,0])
relay4_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(3), grid=[5,2])
relay4_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(3), grid=[5,3])

#Relay #1
relay5_label = Text(app, text="Relay 5", grid=[6,0])
relay5_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(4), grid=[6,2])
relay5_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(4), grid=[6,3])

#Relay #1
relay6_label = Text(app, text="Relay 6", grid=[7,0])
relay6_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(5), grid=[7,2])
relay6_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(5), grid=[7,3])

#Relay #1
relay7_label = Text(app, text="Relay 7", grid=[8,0])
relay7_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(6), grid=[8,2])
relay7_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(6), grid=[8,3])

#Relay #1
relay8_label = Text(app, text="Relay 8", grid=[9,0])
relay8_connect = PushButton(app, text='Connect', command=lambda: switch_relay_on(7), grid=[9,2])
relay8_disconnect = PushButton(app, text='Disconnect', command=lambda: switch_relay_off(7), grid=[9,3])

app.display()