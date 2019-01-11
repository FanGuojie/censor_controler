
"""
:param
    无
:return
    无
功能：调用笔记本摄像头获取视频图片
"""""
import numpy as np
import cv2
from sort.classify_pytorch import initNet,guitest
#调用笔记本内置摄像头，所以参数为0，如果有其他的摄像头可以调整参数为1，2
cap=cv2.VideoCapture(0)
initNet()
i1=0
i2=0
i3=0
while True:
    #从摄像头读取图片
    sucess,img=cap.read()
    #转为灰度图片
    gray=cv2.cvtColor(img,1)
    #显示摄像头，背景是灰度。
    cv2.imshow("img",gray)
    #保持画面的持续。
    k=cv2.waitKey(1)
    if k == 27:
        #通过esc键退出摄像
        cv2.destroyAllWindows()
        break
    elif k==ord("s"):
        #通过s键保存图片，并退出。
        print("sort:")
        cv2.imwrite("sort.jpg",img)
        guitest("sort.jpg")
    elif k==ord("1"):
        #通过1键保存第一类图片
        i1+=1
        print("保存第 一 类图片，第 "+str(i1)+" 张图片")
        cv2.imwrite("../sort/1/"+str(i1)+".png",img)
        # cv2.imwrite("../sort"+str(i1)+".png",img)
    elif k==ord("2"):
        #通过2键保存第二类图片
        i2+=1
        print("保存第 二 类图片，第 "+str(i2)+" 张图片")
        cv2.imwrite("../sort/2/"+str(i2)+".png",img)
    elif k==ord("3"):
        #通过3键保存第三类图片
        i3+=1
        print("保存第 三 类图片，第 "+str(i3)+" 张图片")
        cv2.imwrite("../sort/3/"+str(i3)+".png",img)
    elif(k==ord("t")):
        print("temperature")
        cv2.imwrite("temporature.jpg",img)




#关闭摄像头
cap.release()
