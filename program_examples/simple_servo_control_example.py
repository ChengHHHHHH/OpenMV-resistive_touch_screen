'''
OpenMV电阻式触摸屏扩展板 简单舵机控制示例程序

舵机端口需要独立供电，供电电压不限（不超过舵机额定电压）。
或接入最高5V时，短接Vin和R，舵机和OpenMV同时接受5V供电。

OpenMV4Plus不支持Servo3。

20220318

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
from servo_motor import servo
from time import sleep
'''
定义servo时的可输入参数：
freq 信号频率，默认50Hz，最大380Hz
degrees_max 最大角度，默认180。比如针对于270度舵机可修改为270
degrees_offset 角度补偿，用于增减角度数值与舵机实际对应的关系。注意增减后，最大可控范围会缩小。
signal_limit 信号限制，默认True，即信号脉宽为0.5-2.5ms。修改为False后解除上下限。
'''
s1=servo(1)
s2=servo(2,freq=100)
s3=servo(3,degrees_max=270)
s4=servo(4,degrees_offset=5)
s5=servo(5,signal_limit=False)

while(True):
    s1.degrees(0)
    s2.degrees(45)
    s3.degrees(60)
    s4.degrees(135)
    s5.degrees(180)
    sleep(1)
    s1.degrees(180)
    s2.degrees(135)
    s3.degrees(120)
    s4.degrees(45)
    s5.degrees(0)
    sleep(1)
