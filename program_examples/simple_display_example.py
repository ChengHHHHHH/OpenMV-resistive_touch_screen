'''
OpenMV电阻式触摸屏扩展板 最简示例程序
20220317

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
import sensor, image, time,screen

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

clock = time.clock()    #声明时钟，用于获取帧速

#屏幕初始化。可写入参数：
#screen_baudrate SPI频率，默认80，单位Mhz
#pressure 压力阈值，默认1800，数值越大，需要压力越大
screen.init()

while(True):
    clock.tick()    #时钟记录点，用于获取帧速
    img = sensor.snapshot() #获取感光器画面
    if screen.press:    #如果触屏被按下
        #通过x、y坐标画点
        img.draw_circle(screen.x , screen.y , 3,color=(255,0,0),fill=True)
        img.draw_circle(screen.x , screen.y , 15,color=(255,0,0))
    #屏幕显示图像，同时此函数会获取触摸数值。不运行它，无法更新触屏信息。
    screen.display(img)
    print(clock.fps())  #获取帧速




