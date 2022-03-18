'''
OpenMV电阻式触摸屏扩展板 图像预览与绘图示例程序
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

#创建用于绘图的画布，并填充白色
img_drawing_board=sensor.alloc_extra_fb(320,240,sensor.RGB565)
img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(255,255,255))

fps=0   #帧速变量
last_x=0    #上一次x坐标
last_y=0    #上一次y坐标
first_time_press=True   #第一次按下（抬笔后线条不连续）

while True:
    clock.tick()    #时钟记录点，用于获取帧速
    img = sensor.snapshot() #获取感光器画面
    if screen.press:    #如果触屏被按下
        if first_time_press:    #如果首次按下，绘制一个点
            img_drawing_board.draw_line(screen.x,screen.y,screen.x,screen.y,color=(0,0,0),thickness=3)
            last_x=screen.x #记录本次坐标到‘上一次’变量
            last_y=screen.y
            first_time_press=False  #解除首次标识
        else:   #非首次按下，绘制连续线条
            img_drawing_board.draw_line(screen.x,screen.y,last_x,last_y,color=(0,0,0),thickness=3)
            last_x=screen.x #记录本次坐标到‘上一次’变量
            last_y=screen.y
    else:
        first_time_press=True   #置首次标识
    img.b_nor(img_drawing_board)    #将画板画布与感光器图像叠加
    img.draw_string(10,10,'FPS:'+str(fps),color=(255,0,0),mono_space=False)    #绘制帧速
    screen.display(img) #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。
    fps=clock.fps() #获取帧速




