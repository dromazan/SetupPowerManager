from tkinter import *
import sys
import glob
import serial
import time
from PIL import Image, ImageTk
import queue
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from random import uniform
import numpy as np

r_label = ['USB HUB', 'MAIN CAM', 'FOCUSER', 'FAN', 'S.M. HEAT', 'F.WHEEL', 'CAM HEAT', 'OAG HEAT']
voltage_list = []
current_list = []
t_ambient_list = []
t_mirror_list = []

# for plotting test
# for i in range(360):
#     voltage_list.append(uniform(11.4, 12.6))
#     current_list.append(uniform(0.5, 3.7))


class SerialThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self._stop_event = threading.Event()

    def run(self):
        global ser
        while not self.stopped():
            if ser.is_open:
                text = ser.read()
                text = serial.unicode(text, errors='ignore')
                print('serial received - %s' % text)
                self.queue.put(text)
                process_queue()
            else:
                self.stop()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def process_queue():
    global queue
    while queue.qsize():
        try:
            msg = queue.get()
            print('from queue msg - %s' % msg)
            if msg.startwith("v"):
                voltage = float(msg[1:])
                voltage_list.append(voltage)
                if len(voltage_list) > 720:
                    voltage_list.pop(0)
            elif msg.startwith("c"):
                current = float(msg[1:])
                current_list.append(current)
                if len(current_list) > 720:
                    current_list.pop(0)
            elif msg.startwith("a"):
                t_ambient = float(msg[1:])
                t_ambient_list.append(t_ambient)
                if len(t_ambient_list) > 720:
                    t_ambient_list.pop(0)
            elif msg.startwith("m"):
                t_mirror = float(msg[1:])
                t_mirror_list.append(t_mirror)
                if len(t_mirror_list) > 720:
                    t_ambient_list.pop(0)
            elif len(msg) == 8:
                upd_power_icons(msg)

        except queue.Empty:
            # just on general principles, although we don't
            # expect this branch to be taken in this case
            pass


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
    ser.port = var.get()
    ser.open()
    if ser.is_open:
        print('port is connected')
        time.sleep(2)
        conn_state_label.configure(image=port_state_img_connected)
        master.update()
        request_state()
    else:
        conn_state_label.configure(image=port_state_img_disconnected)
        master.update()


def close_port():
    ser.close()
    if ser.is_open:
        conn_state_label.configure(image=port_state_img_connected)
        master.update()
    else:
        conn_state_label.configure(image=port_state_img_disconnected)
        master.update()
        for i in range(0, 8):
            power_state_label[i].configure(image=power_state_img_off)
            master.update()
        print('port is disconnected')


def send_command(relay, param):
    request = '{}{}'.format(relay, param)
    print(request)
    print(request.encode(encoding='UTF-8'))
    ser.write(request.encode(encoding='UTF-8'))


def switch_relay_on(relay):
    send_command(relay, '1')

    power_state_label[relay].configure(image=power_state_img_on)
    master.update()


def switch_relay_off(relay):
    send_command(relay, '0')

    power_state_label[relay].configure(image=power_state_img_off)
    master.update()


def request_state():
    request = '!!'
    ser.write(request.encode(encoding='UTF-8'))
    # pins_state_str = ser.readline().decode("utf-8")
    # print(pins_state_str)
    # # pins = list(pins_state_str)
    # print(pins_state_str)


def upd_power_icons(pins_state_str):
    for i, l in enumerate(pins_state_str):
        if l == '0':
            power_state_label[i].configure(image=power_state_img_off)
            master.update()
            i += 1
        elif l == '1':
            power_state_label[i].configure(image=power_state_img_on)
            master.update()
            i += 1


def expand_master():
    print(show_graph.get())
    if show_graph.get() == 1:
        print('changing width to 900')
        mf.configure(width=900)
        #mf.pack_propagate(0)
        master.update()
    elif show_graph.get() == 0:
        print('changing width to 400')
        mf.configure(width=400)
        #mf.pack_propagate(0)
        master.update()


def plot_power_chart(t_ambient, t_mirror):
    my_dpi = 144
    fig = Figure(figsize=(3.2, 2), dpi=144)
    fig.subplots_adjust(0., 0.1, 0.8, 1.)

    line1, = fig.add_subplot(111).plot(t_ambient, color='red', linewidth=0.5, label='ambient')
    line2, = fig.add_subplot(111).plot(t_mirror, color='green', linewidth=0.5, label='mirror')
    fig.add_subplot(111).set_xticklabels(np.arange(0, len(t_mirror), step=50), fontdict={'fontsize': 5})
    fig.add_subplot(111).grid()
    fig.add_subplot(111).legend(bbox_to_anchor=(1., 1), handles=[line1, line2], loc=2, fontsize=5)
    canvas = FigureCanvasTkAgg(fig, master=power_graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)


    # toolbar = NavigationToolbar2TkAgg(canvas, power_graph_frame)
    # toolbar.update()
    # canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

def plot_temp_chart():
    pass

master = Tk()
master.resizable(False, False)
master.title("Setup PowerManagement")
mf = Frame(master, height=340, width=400)
mf.pack_propagate(0)  # don't shrink
mf.pack()

port_label = Label(master, text="Select Port:", font=("Helvetica", 10))
port_label.place(x=5, y=10)

var = StringVar(master)
var.set(ports[0])  # initial value
print('var is %s' % var)

# Selec port drop down
option_frame = Frame(master, height=30, width=100)
option_frame.pack_propagate(0)  # don't shrink
option_frame.pack()
option_frame.place(x=90, y=5)
option = OptionMenu(option_frame, var, *ports)
option.pack(fill=BOTH)

# Connect button
conn_btn_frame = Frame(master, height=30, width=80)
conn_btn_frame.pack_propagate(0)  # don't shrink
conn_btn_frame.pack()
conn_btn_frame.place(x=195, y=2)
connect_btn = Button(conn_btn_frame, text='Connect', command=lambda: open_port())
connect_btn.pack(fill=BOTH, expand=1)

# Disconnect button
disconn_btn_frame = Frame(master, height=30, width=80)
disconn_btn_frame.pack_propagate(0)  # don't shrink
disconn_btn_frame.pack()
disconn_btn_frame.place(x=280, y=2)
disconnect_btn = Button(disconn_btn_frame, text='Disconnect', command=lambda: close_port())
disconnect_btn.pack(fill=BOTH, expand=1)

# Connection state icon
port_state_ico_connected = Image.open("connected.png")
port_state_ico_disconnected = Image.open("disconnected.png")

port_state_img_connected = ImageTk.PhotoImage(port_state_ico_connected)
port_state_img_disconnected = ImageTk.PhotoImage(port_state_ico_disconnected)

conn_state_label = Label(master, image=port_state_img_disconnected)
conn_state_label.place(x=365, y=2)

for label in r_label:
    print(label)
    print(r_label.index(label))
    Label(master, text=label, font=("Helvetica", 10)).place(x=5, y=50 + r_label.index(label) * 35)

# ON BUTTONS
on_frame0 = Frame(master, height=30, width=50)
on_frame1 = Frame(master, height=30, width=50)
on_frame2 = Frame(master, height=30, width=50)
on_frame3 = Frame(master, height=30, width=50)
on_frame4 = Frame(master, height=30, width=50)
on_frame5 = Frame(master, height=30, width=50)
on_frame6 = Frame(master, height=30, width=50)
on_frame7 = Frame(master, height=30, width=50)

on_frame = [on_frame0,
             on_frame1,
             on_frame2,
             on_frame3,
             on_frame4,
             on_frame5,
             on_frame6,
             on_frame7]

on_btn0 = Button(on_frame0, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(0))
on_btn1 = Button(on_frame1, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(1))
on_btn2 = Button(on_frame2, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(2))
on_btn3 = Button(on_frame3, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(3))
on_btn4 = Button(on_frame4, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(4))
on_btn5 = Button(on_frame5, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(5))
on_btn6 = Button(on_frame6, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(6))
on_btn7 = Button(on_frame7, text='ON', font=("Helvetica", 10), command=lambda: switch_relay_on(7))

on_btn =[on_btn0,
          on_btn1,
          on_btn2,
          on_btn3,
          on_btn4,
          on_btn5,
          on_btn6,
          on_btn7]


# OFF BUTTONS
off_frame0 = Frame(master, height=30, width=50)
off_frame1 = Frame(master, height=30, width=50)
off_frame2 = Frame(master, height=30, width=50)
off_frame3 = Frame(master, height=30, width=50)
off_frame4 = Frame(master, height=30, width=50)
off_frame5 = Frame(master, height=30, width=50)
off_frame6 = Frame(master, height=30, width=50)
off_frame7 = Frame(master, height=30, width=50)

off_frame = [off_frame0,
             off_frame1,
             off_frame2,
             off_frame3,
             off_frame4,
             off_frame5,
             off_frame6,
             off_frame7]

off_btn0 = Button(off_frame0, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(0))
off_btn1 = Button(off_frame1, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(1))
off_btn2 = Button(off_frame2, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(2))
off_btn3 = Button(off_frame3, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(3))
off_btn4 = Button(off_frame4, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(4))
off_btn5 = Button(off_frame5, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(5))
off_btn6 = Button(off_frame6, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(6))
off_btn7 = Button(off_frame7, text='OFF', font=("Helvetica", 10), command=lambda: switch_relay_off(7))

off_btn =[off_btn0,
          off_btn1,
          off_btn2,
          off_btn3,
          off_btn4,
          off_btn5,
          off_btn6,
          off_btn7]


# #Relay img
# relay_ico = Image.open('relay.png')
# relay_img = ImageTk.PhotoImage(relay_ico)
#
# relay_frame = Frame(master, height=200, width=109)
# relay_label = Label(relay_frame, image=relay_img)
# relay_label.pack()
# relay_frame.pack()
# relay_frame.place(x=275, y=50)

# On/Off icon
power_state_icon_off = Image.open('off.png')
power_state_icon_on = Image.open('on.png')

power_state_img_on = ImageTk.PhotoImage(power_state_icon_on)
power_state_img_off = ImageTk.PhotoImage(power_state_icon_off)

power_state_frame0 = Frame(master, height=30, width=30, bg='red')
power_state_frame1 = Frame(master, height=30, width=30, bg='red')
power_state_frame2 = Frame(master, height=30, width=30, bg='red')
power_state_frame3 = Frame(master, height=30, width=30, bg='red')
power_state_frame4 = Frame(master, height=30, width=30, bg='red')
power_state_frame5 = Frame(master, height=30, width=30, bg='red')
power_state_frame6 = Frame(master, height=30, width=30, bg='red')
power_state_frame7 = Frame(master, height=30, width=30, bg='red')

power_state_frame = [power_state_frame0,
                     power_state_frame1,
                     power_state_frame2,
                     power_state_frame3,
                     power_state_frame4,
                     power_state_frame5,
                     power_state_frame6,
                     power_state_frame7]

power_state_label0 = Label(power_state_frame0, image=power_state_img_off)
power_state_label1 = Label(power_state_frame1, image=power_state_img_off)
power_state_label2 = Label(power_state_frame2, image=power_state_img_off)
power_state_label3 = Label(power_state_frame3, image=power_state_img_off)
power_state_label4 = Label(power_state_frame4, image=power_state_img_off)
power_state_label5 = Label(power_state_frame5, image=power_state_img_off)
power_state_label6 = Label(power_state_frame6, image=power_state_img_off)
power_state_label7 = Label(power_state_frame7, image=power_state_img_off)

power_state_label =[power_state_label0,
                    power_state_label1,
                    power_state_label2,
                    power_state_label3,
                    power_state_label4,
                    power_state_label5,
                    power_state_label6,
                    power_state_label7]

for i in range(0, 8):
    on_frame[i].pack_propagate(0)
    on_frame[i].pack()
    on_frame[i].place(x=100, y=50 + i * 35)
    on_btn[i].pack(fill=BOTH, expand=1)
    off_frame[i].pack_propagate(0)
    off_frame[i].pack()
    off_frame[i].place(x=155, y=50 + i * 35)
    off_btn[i].pack(fill=BOTH, expand=1)
    power_state_label[i].pack()
    power_state_frame[i].pack()
    power_state_frame[i].place(x=210, y=50 + i * 35)

power_lable = Label(master, text="Power State:", font=("Helvetica", 12))
power_lable.place(x=275, y=50)

voltage_label = Label(master, text = "Voltage = %s V" % "N/A")
voltage_label.place(x=275, y=80)

current_label = Label(master, text="Current = %s A" % "N/A")
current_label.place(x=275, y=110)

temp_label = Label(master, text="Temperature:", font=("Helvetica", 12))
temp_label.place(x=275, y=150)

ambient_t_label = Label(master, text = "T Ambient = %s C" % "N/A")
ambient_t_label.place(x=275, y=180)

mirror_t_label = Label(master, text="T Mirror = %s C" % "N/A")
mirror_t_label.place(x=275, y=210)

show_graph = IntVar()
show_graph_cbox = Checkbutton(master, text="Show graphs", variable=show_graph, command=expand_master)
show_graph_cbox.place(x=275, y=300)

power_graph_label = Label(master, text='Temperature:', font=('Helvetice', 12))
power_graph_label.place(x=420, y=2)


power_graph_frame = Frame(master, width=465, height=300, bd=3)
power_graph_frame.place(x=420, y=25)

plot_power_chart(t_ambient_list, t_mirror_list)

queue = queue.Queue()

mainloop()
