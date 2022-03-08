import pyb
import task_share
import time

limit1_share = task_share.Share('i', thread_protect = False, name = "Limit 1 Share")
limit2_share = task_share.Share('i', thread_protect = False, name = "Limit 2 Share")

limit1_share.put(0)
limit2_share.put(0)

def cb1(e):
    print('interrupted')
    limit1_share.put(1)
    lim1.disable()
def cb2(e):
    limit2_share.put(1)
    lim2.disable()

lim1 = pyb.ExtInt(pyb.Pin.cpu.C3, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_NONE, cb1)
lim2 = pyb.ExtInt(pyb.Pin.cpu.C2, pyb.ExtInt.IRQ_FALLING, pyb.Pin.PULL_NONE, cb2)

while True:
    print(limit1_share.get(), limit2_share.get())
    time.sleep(0.2)