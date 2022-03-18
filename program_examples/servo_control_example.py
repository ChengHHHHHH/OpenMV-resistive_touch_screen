'''
OpenMV电阻式触摸屏扩展板 舵机控制示例程序

舵机端口需要独立供电，供电电压不限（不超过舵机额定电压）。
或接入最高5V时，短接Vin和R，舵机和OpenMV同时接受5V供电。

OpenMV4Plus不支持Servo3，运行此程序时，屏幕中Servo3的指针为红色

本程序比较复杂，对于舵机用法的理解，可以参考简单舵机示例程序
对于触屏的理解和使用，可以参考本程序的逻辑

20220318

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
import sensor, image, time, screen, math
from servo_motor import servo

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

screen.init()#初始化屏幕

clock = time.clock()
img=sensor.alloc_extra_fb(320,240,sensor.RGB565)
coordinates=[(260,60),(160,60),(60,60),(160,170),(60,170)]  #5个控制区的中心坐标
degrees=[0,0,0,0,0] #5路舵机的角度
degrees_max=[180,180,270,180,180]   #5路舵机的最大角度
degrees_offset=[0,0,0,0,0]  #5路舵机的中点补偿

r=32    #指针半径
a=40    #方形轮廓边长
#指针颜色
line_color=[(255,255,255),(255,255,255),(255,255,255),(255,255,255),(255,255,255)]
s=[0,0,0,0,0]#要声明的舵机
#注意！servo库的声明要在screen.init()之后
#因为与官方屏幕库共用了IO，后初始化屏幕会导致IO功能异常。
for n in range(5):  #声明舵机
    try:
        s[n]=servo(n+1,degrees_max=degrees_max[n],degrees_offset=degrees_offset[n])
    except: #如果声明失败，则可能是4plus不支持的Servo3
        line_color[n]=(255,0,0) #此路指针赋红色
while(True):
    clock.tick()
    img.clear()
    for n in range(5):
        #画方框、文字、指针
        img.draw_rectangle(coordinates[n][0]-a,coordinates[n][1]-a,80,80)
        img.draw_string(coordinates[n][0]-a+10,coordinates[n][1]+a+5,'Servo '+str(n+1))
        img.draw_line(coordinates[n][0],coordinates[n][1],\
            coordinates[n][0]-round(math.sin((degrees[n]-90)/180*math.pi)*r),\
            coordinates[n][1]-round(math.cos((degrees[n]-90)/180*math.pi)*r) ,\
            color=line_color[n],thickness=4)
        #在每个方框中获取触摸的角度
        if screen.press:
            if coordinates[n][0]-a<screen.x<coordinates[n][0]+a and\
            coordinates[n][1]-a<screen.y<coordinates[n][1]+a:
                if screen.x<coordinates[n][0]:  #第二 第三 象限
                    degrees_single=math.atan((screen.y-coordinates[n][1])/(screen.x-coordinates[n][0]))/math.pi*180
                    if screen.y<coordinates[n][1]:  #第二象限
                        degrees_single=180-degrees_single
                    elif screen.y>coordinates[n][1]:    #第三象限
                        degrees_single=180-degrees_single
                    else:
                        degrees_single=180    #x负半轴上
                elif screen.x>coordinates[n][0]:    #第一 第四象限
                    degrees_single=math.atan((screen.y-coordinates[n][1])/(screen.x-coordinates[n][0]))/math.pi*180
                    if screen.y<coordinates[n][1]:  #第一象限
                        degrees_single*=-1
                    elif screen.y>coordinates[n][1]:    #第四象限
                        degrees_single=360-degrees_single
                    else:   #x正半轴上
                        degrees_single=0
                else:   #y轴上
                    if screen.y<coordinates[n][1]:  #y的正半轴
                        degrees_single=90
                    elif screen.y>coordinates[n][1]:#y的负半轴
                        degrees_single=270
                    else:   #原点
                        pass
                if degrees_single<degrees_max[n]:
                    line_color[n]=(255,255,255)
                    try:
                        s[n].degrees(degrees[n]) #指定舵机转动
                    except:
                        line_color[n]=(255,0,0) #执行失败则指针变红（4Plus的Servo3）
                else:
                    line_color[n]=(255,0,0) #超过最大角度后，指针变红
                degrees[n]=degrees_single   #角度装填，以备显示

    screen.display(img)
    print(clock.fps())
