'''
OpenMV电阻式触摸屏扩展板 显示与触摸库

因为触摸IC与屏幕共用SPI，所以不能开启官方库的三重缓冲功能
测试帧速如下：
    固件4.3.0，感光器QVGA图像预览，高亮环境：
        OpenMV4 30帧+
        OpenMV4Plus 45帧+
    固件4.3.0，感光器停止，仅刷新图像(如画图例程)：
        50帧+

首次运行，会执行触摸校准程序，校准完成后，会在本地根目录生成 calibration.py 文件
如需重新校准，删除 calibration.py 即可

程序库调用方法详见示例程序，或与我联系

20220317

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
import lcd
from pyb import Pin, SPI, millis,hard_reset
import struct
from sensor import alloc_extra_fb,snapshot,RGB565
from time import sleep
x=0
y=0
z=0
press=False
x_original=0
y_original=0
z_original=0
press_threshold=2800
                #x_min,x_max,x_step
calibration_data=[29532,796,-89.8,\
                #y_min,y_max,y_step
                1976,30872,120.4,\
                #6:z_min,7:z_max,8:z_x_step,9:z_y_step
                27492.0, 17716, -35.0, 10.8667]
calibration_coordinate=((80,60),(240,60),(80,180),(240,180))
baudrate=80

spi2=SPI(2,SPI.MASTER,baudrate=40*1000000,phase=1)
CS = Pin('P3', Pin.OUT_PP)
RS = Pin('P8', Pin.OUT_PP)

def write_c(c):
    CS.low()
    RS.low()
    spi2.send(c)
    CS.high()

def write_d(c):
    CS.low()
    RS.high()
    spi2.send(c)
    CS.high()

def write_command(c, *data):
    write_c(c)
    if data:
        for d in data:
            write_d(d)

def set_resolution(x,y,w,h):
    write_c(0x2a)
    write_d(int(x/256))
    write_d(x%256)
    write_d(int((x+w-1)/256))
    write_d((x+w-1)%256)
    write_c(0x2b)
    write_d(int(y/256))
    write_d(y%256)
    write_d(int((y+h-1)/256))
    write_d((y+h-1)%256)
    write_c(0x2C)

#baudrate 设置屏幕通讯频率，频率越高刷新效果越好，但高频可能导致显示异常
def init(screen_baudrate=80,pressure=1800):
    global calibration_data,baudrate,press_threshold
    press_threshold=5000-pressure
    lcd.init(width=320,height=240,triple_buffer=False,rbg=True)
    write_c(0x36)#设置屏幕方向
    write_d(0xa0)
    set_resolution(0,0,320,240)#设置屏幕分辨率
    baudrate=screen_baudrate
    try:
        import calibration
        calibration_data=calibration.data
    except:
        #pass
        touch_calibration()

def touch_calibration():
    global calibration_data,x_original,y_original,z_original
    x_record=[]
    y_record=[]
    z_record=[]
    img=alloc_extra_fb(320,240,RGB565)
    img.draw_string(115,110,'screen calibration',mono_space=False)
    display(img)
    lcd.display(img,x_size=320)

    timer=millis()
    for n in range(0,4):
        while True:
            display(img)
            img.clear()
            #有触摸
            if x_original<32700 and y_original>100:
                img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],4,fill=True)
                img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],13,color=(255,255,0))
                img.draw_string(calibration_coordinate[n][0]-4,calibration_coordinate[n][1]-25,str(3-round((millis()-timer)/1000)))
                if millis()-timer>3000:
                    x_record.append(x_original)
                    y_record.append(y_original)
                    z_record.append(z_original)
                    img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],4,fill=True)
                    img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],13,color=(0,255,0))
                    lcd.display(img,x_size=320)
                    while x_original<32700 or y_original>100:
                        display(img)
                    sleep(0.5)
                    break
            else:
                timer=millis()
                img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],4,fill=True)
                img.draw_circle(calibration_coordinate[n][0],calibration_coordinate[n][1],13,color=(255,0,0))
            img.draw_string(115,110,'screen calibration',mono_space=False)
        display(img)
        print(x_record)
        print(y_record)
        print(z_record)

    x_step=(((x_record[1]-x_record[0])/(calibration_coordinate[1][0]-calibration_coordinate[0][0]))+\
        ((x_record[3]-x_record[2])/(calibration_coordinate[3][0]-calibration_coordinate[2][0])))/2
    x_min=((x_record[0]-calibration_coordinate[0][0]*x_step)+\
        (x_record[1]-calibration_coordinate[1][0]*x_step)+\
        (x_record[2]-calibration_coordinate[2][0]*x_step)+\
        (x_record[3]-calibration_coordinate[3][0]*x_step))/4
    x_max=((x_record[0]+(320-calibration_coordinate[0][0])*x_step)+\
        (x_record[1]+(320-calibration_coordinate[1][0])*x_step)+\
        (x_record[2]+(320-calibration_coordinate[2][0])*x_step)+\
        (x_record[3]+(320-calibration_coordinate[3][0])*x_step))/4

    y_step=(((y_record[2]-y_record[0])/(calibration_coordinate[2][1]-calibration_coordinate[0][1]))+\
        ((y_record[3]-y_record[1])/(calibration_coordinate[3][1]-calibration_coordinate[1][1])))/2
    y_min=((y_record[0]-calibration_coordinate[0][1]*y_step)+\
        (y_record[1]-calibration_coordinate[1][1]*y_step)+\
        (y_record[2]-calibration_coordinate[2][1]*y_step)+\
        (y_record[3]-calibration_coordinate[3][1]*y_step))/4
    y_max=((y_record[0]+(240-calibration_coordinate[0][1])*y_step)+\
        (y_record[1]+(240-calibration_coordinate[1][1])*y_step)+\
        (y_record[2]+(240-calibration_coordinate[2][1])*y_step)+\
        (y_record[3]+(240-calibration_coordinate[3][1])*y_step))/4

    z_x_step=(((z_record[1]-z_record[0])/(calibration_coordinate[1][0]-calibration_coordinate[0][0]))+\
        ((z_record[3]-z_record[2])/(calibration_coordinate[3][0]-calibration_coordinate[2][0])))/2
    z_y_step=(((z_record[2]-z_record[0])/(calibration_coordinate[2][1]-calibration_coordinate[0][1]))+\
        ((z_record[3]-z_record[1])/(calibration_coordinate[3][1]-calibration_coordinate[1][1])))/2
    z_min=((z_record[0]-calibration_coordinate[0][0]*z_x_step-calibration_coordinate[0][1]*z_y_step)+\
        (z_record[1]-calibration_coordinate[1][0]*z_x_step-calibration_coordinate[1][1]*z_y_step)+\
        (z_record[2]-calibration_coordinate[2][0]*z_x_step-calibration_coordinate[2][1]*z_y_step)+\
        (z_record[3]-calibration_coordinate[3][0]*z_x_step-calibration_coordinate[3][1]*z_y_step))/4
    z_max=((z_record[0]+(320-calibration_coordinate[0][0])*z_x_step+(240-calibration_coordinate[0][1])*z_y_step)+\
        (z_record[1]+(320-calibration_coordinate[1][0])*z_x_step+(240-calibration_coordinate[1][1])*z_y_step)+\
        (z_record[2]+(320-calibration_coordinate[2][0])*z_x_step+(240-calibration_coordinate[2][1]*z_y_step))+\
        (z_record[3]+(320-calibration_coordinate[3][0])*z_x_step+(240-calibration_coordinate[3][1]*z_y_step)))/4
    calibration_data=[x_min,x_max,x_step,y_min,y_max,y_step,z_min,z_max,z_x_step,z_y_step]

    f = open('calibration.py',mode='a+')
    f.write('data='+str(calibration_data))
    sleep(0.5)
    f.close()
    hard_reset()
    print(calibration_data)

def display(img):
    global x,y,z,calibration_data,baudrate,press,\
            x_original,y_original,z_original,press_threshold
    CS.low()
    spi = SPI(2, SPI.MASTER,baudrate=2*1000000,phase=1)

    spi.send(0x90)
    recv1=spi.recv(1)
    recv2=spi.recv(1)
    x_original=struct.unpack('B',recv1)[0]*256+struct.unpack('B',recv2)[0]
    x=round(( ((x_original-calibration_data[0])/calibration_data[2]) + \
        (320-((calibration_data[1]-x_original)/calibration_data[2])) )/2)
    if x<0 or x>320:
        x=-1

    spi.send(0xd0)
    recv1=spi.recv(1)
    recv2=spi.recv(1)
    y_original=struct.unpack('B',recv1)[0]*256+struct.unpack('B',recv2)[0]
    y=round(( ((y_original-calibration_data[3])/calibration_data[5]) + \
        (240-((calibration_data[4]-y_original)/calibration_data[5])) )/2)
    if y<0 or y>320:
        y=-1
    if x>-1 and y>-1:
        spi.send(0xc0)
        recv1=spi.recv(1)
        recv2=spi.recv(1)
        z_original=struct.unpack('B',recv1)[0]*256+struct.unpack('B',recv2)[0]
        z=calibration_data[6]+press_threshold-round( (z_original - x**1.02*calibration_data[8] - y*1.02*calibration_data[9]))
        if z<0:
            x=-1
            y=-1
            press=False
        else:
            press=True
    else:
        press=False
    spi = SPI(2, SPI.MASTER,baudrate=baudrate*1000000,phase=1)

    lcd.display(img,x_size=320)

