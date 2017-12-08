import tkinter as tk
import time as tm
import math as m
import RPi.GPIO as gp

# runMinutes is a 7 element list where 0 is Monday
# start_time is a time in the format (24 hour) HH:MM
class onOffController:
    (ON, OFF) = (1,0)
    def __init__(self):
        self.label_text = 'controller'
        self.grid_row = 0
        self.gpioPinNum = 2
        self.run_times = [0, 0, 0, 0, 0, 0, 0]
        self.start_time = ''
        self.manualRun = False

    def run_minutes(self):
        today = tm.localtime()
        return self.run_times[today.tm_wday]

    def start(self):
        st = tm.strptime(self.start_time, '%H:%M')
        return st

    def status(self):
        cur_min = tm.localtime().tm_hour * 60 + tm.localtime().tm_min
        start_min = self.start().tm_hour * 60 + self.start().tm_min
        stop_min = start_min + self.run_minutes()
        if cur_min >= start_min and cur_min < stop_min:
            return self.ON
        else:
            return self.OFF

class sinusoidalController:
    (ON, OFF) = (1,0)
    def __init__(self):
        self.label_text = 'controller'
        self.grid_row = 0
        self.gpioPinNum = 2
        self.start_time = ''
        self.long_day_minutes = 720 # 12 hrs
        self.short_day_minutes = 600 # 10 hrs
        self.longest_day = 172 # Jan-01 is day 1, Jun-21 is day 172
        self.manualRun = False
        
    def start(self):
        st = tm.strptime(self.start_time, '%H:%M')
        return st
    
    def run_minutes(self):
        pi = 3.1416
        day = tm.localtime().tm_yday - self.longest_day
        myConst = 365 / (pi / 2 * 4)
        rng_frac = (m.cos(day / myConst) + 1) / 2 # varies from 0 to +1
        run_mins = m.floor(self.short_day_minutes + rng_frac * (self.long_day_minutes - self.short_day_minutes))
        return run_mins
        
    def status(self):
        cur_min = tm.localtime().tm_hour * 60 + tm.localtime().tm_min
        start_min = self.start().tm_hour * 60 + self.start().tm_min
        stop_min = start_min + self.run_minutes()
        if cur_min >= start_min and cur_min < stop_min:
            return self.ON
        else:
            return self.OFF
 
def toggleManualRun(c):
    if c.manualRun ==False:
        c.manualRun = True
    else:
        c.manualRun = False
    
    
# setup objects to control outlets
o1 = onOffController()
o1.label_text = 'Sprayers'
o1.grid_row = 6
o1.gpioPinNum = 2
o1.run_times = [10, 10, 10, 10, 10, 10, 10]
o1.start_time = '8:00'

o2 = onOffController()
o2.label_text = 'Tray'
o2.grid_row = 7
o2.gpioPinNum = 3
o2.run_times = [10, 0, 0, 10, 0, 0, 0]
o2.start_time = '9:00'

o3 = sinusoidalController()
o3.label_text = 'Lights'
o3.grid_row = 8
o3.gpioPinNum = 4
o3.start_time = '8:00'
o3.long_day_minutes = 840
o3.short_day_minutes = 600
o3.longest_day = 170

o4 = onOffController()
o4.label_text = 'Manual Only'
o4.grid_row = 9
o4.gpioPinNum = 17
o4.run_times = [0, 0, 0, 0, 0, 0, 0]
o4.start_time = '0:00'

outlets = [o1, o2, o3, o4]  # allows them to be iterated over

# GUI Setup
# some initializations
root = tk.Tk()
root.title('My Grow Controller')
x_pad = 4
y_pad = 2
red_light = tk.PhotoImage(file='red_light.gif')
green_light = tk.PhotoImage(file='green_light.gif')
green_light_man = tk.PhotoImage(file='green_light_manual.gif')
col_nums = {'label': 0, 'status': 1, 'run_mins': 2, 'start_time': 3, 'button': 4}

gp.setwarnings(False)
gp.setmode(gp.BCM)
gp.setup(o1.gpioPinNum, gp.OUT)
gp.setup(o2.gpioPinNum, gp.OUT)
gp.setup(o3.gpioPinNum, gp.OUT)
gp.setup(o4.gpioPinNum, gp.OUT)

cur_date = tk.StringVar()
cur_time = tk.StringVar()
cur_date.set(tm.strftime('%a %b %d', tm.localtime()))
cur_time.set(tm.strftime('%I:%M:%S', tm.localtime()))

# header
tk.Label(root, text = 'Grow Controller Status', font='-weight normal').grid(row=0, column=0, sticky=tk.W, columnspan=2, padx=x_pad, pady=y_pad)
tk.Label(root, text='Date:', font='-weight normal').grid(row=2, column=0, sticky=tk.W, padx=x_pad, pady=y_pad)
tk.Label(root, textvariable=cur_date).grid(row=2, column=1, sticky=tk.W, padx=x_pad, pady=y_pad)
tk.Label(root, text='Time:', font='-weight normal').grid(row=3, column=0, sticky=tk.W, padx=x_pad, pady=y_pad)
tk.Label(root, textvariable=cur_time).grid(row=3, column=1, sticky=tk.W, padx=x_pad, pady=y_pad)

# column labels
tk.Label(root, text='Status', font='-weight normal').grid(row=5, column=1, padx=x_pad, pady=y_pad)
tk.Label(root, text='Run Minutes', font='-weight normal').grid(row=5, column=2, padx=x_pad, pady=y_pad)
tk.Label(root, text='Start Time', font='-weight normal').grid(row=5, column=3, padx=x_pad, pady=y_pad)

# outlet details
lights = []
rmins = []
st_times = []
for o in range(len(outlets)):
    tk.Label(root, text=outlets[o].label_text, font='-weight normal').grid(row=outlets[o].grid_row, column=col_nums['label'], sticky=tk.W,
                                                                  padx=x_pad, pady=y_pad)
    thisLight = tk.Label(root, image=red_light)
    lights.append(thisLight)
    thisLight.grid(row=outlets[o].grid_row, column=col_nums['status'], padx=x_pad, pady=y_pad)

    this_rmin = tk.Label(root, text=int(outlets[o].run_minutes()))
    rmins.append(this_rmin)
    this_rmin.grid(row=outlets[o].grid_row, column=col_nums['run_mins'], padx=x_pad, pady=y_pad)

    this_st_time = tk.Label(root, text=outlets[o].start_time)
    st_times.append(this_st_time)
    this_st_time.grid(row=outlets[o].grid_row, column=col_nums['start_time'], padx=x_pad, pady=y_pad)

# button to toggle manual on/off
b1 =tk.Button(root, text='Manual', command=lambda:toggleManualRun(o1)).grid(row=o1.grid_row, column=col_nums['button'], sticky=tk.W, padx=x_pad, pady=y_pad)
b2 =tk.Button(root, text='Manual', command=lambda:toggleManualRun(o2)).grid(row=o2.grid_row, column=col_nums['button'], sticky=tk.W, padx=x_pad, pady=y_pad)
b4 =tk.Button(root, text='Manual', command=lambda:toggleManualRun(o4)).grid(row=o4.grid_row, column=col_nums['button'], sticky=tk.W, padx=x_pad, pady=y_pad)

while True:
    tm.sleep(1)
    cur_date.set(tm.strftime('%a %b %d', tm.localtime()))
    cur_time.set(tm.strftime('%I:%M:%S', tm.localtime()))
    # Note: when i did the wiring of the relays I think I got the pins confused.  Rather than re-wire I just change the 
    # outputs so that LOW is on and HIGH is off
    for o in range(len(outlets)):
        if outlets[o].manualRun == True:
            lights[o].config(image = green_light_man)
            gp.output(outlets[o].gpioPinNum, gp.HIGH)
            
        elif outlets[o].status() == 1:
            lights[o].config(image = green_light)
            gp.output(outlets[o].gpioPinNum, gp.HIGH)
            
        else:
            lights[o].config(image = red_light)
            gp.output(outlets[o].gpioPinNum, gp.LOW)

        rmins[o].config(text=int(outlets[o].run_minutes()))
        st_times[o].config(text=outlets[o].start_time)

    root.update()

root.mainloop()

