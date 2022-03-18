'''
OpenMV电阻式触摸屏扩展板 舵机库

注意！servo库的声明要在screen.init()之后
因为与官方屏幕库共用了IO，后初始化屏幕会导致IO功能异常。

servo1-3是板上端口
servo4、5是uart的Txd、Rxd（需自主接线）
就是说，不使用uart的话，最多可以接5路舵机

OpenMV4P不支持servo3！
OpenMV4支持全部5个舵机端口

舵机端口需要独立供电，供电电压不限（不超过舵机额定电压）。
或接入最高5V时，短接Vin和R，舵机和OpenMV同时接受5V供电。

程序库调用方法详见示例程序，或与我联系

20220317

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
from pyb import Servo
from pyb import Pin,Timer
from time import sleep

class servo():
    def __init__(self,channel,freq=50,degrees_max=180,degrees_offset=0,signal_limit=True):
        if freq<50:
            freq=50
        if freq>380:
            freq=380
        self.degrees_offset=degrees_offset
        self.degrees_max=degrees_max
        self.signal_limit=signal_limit
        if channel==1:
            self.tim = Timer(2, freq=freq)
            self.pwm_output = self.tim.channel(1, Timer.PWM, pin=Pin("P6"), pulse_width_percent=100)
        elif channel==2:
            self.tim = Timer(4, freq=freq)
            self.pwm_output = self.tim.channel(1, Timer.PWM, pin=Pin("P7"), pulse_width_percent=100)
        elif channel==3:
            self.tim = Timer(4, freq=freq)
            self.pwm_output = self.tim.channel(3, Timer.PWM, pin=Pin("P9"), pulse_width_percent=100)
        elif channel==4:
            self.tim = Timer(2, freq=freq)
            self.pwm_output = self.tim.channel(3, Timer.PWM, pin=Pin("P4"), pulse_width_percent=100)
        elif channel==5:
            self.tim = Timer(2, freq=freq)
            self.pwm_output = self.tim.channel(4, Timer.PWM, pin=Pin("P5"), pulse_width_percent=100)

        self.pulse_width_tot=self.pwm_output.pulse_width()
        self.pulse_width_min=self.pulse_width_tot/(1000/freq)*0.5    #最小脉宽0.5ms
        self.pulse_width_max=self.pulse_width_tot/(1000/freq)*2.5    #最大脉宽2.5ms
        self.pulse_width_step=(self.pulse_width_max-self.pulse_width_min)/degrees_max    #脉宽步进值
        self.degrees(self.degrees_max/2)

    def degrees(self,d):
        d+=self.degrees_offset
        if self.signal_limit:
            if d<0:
                d=0
            elif d>self.degrees_max:
                d=self.degrees_max
        self.pwm_output.pulse_width(round(self.pulse_width_min+d*self.pulse_width_step))

