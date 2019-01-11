
from PIL import Image
from PIL import ImageFilter
from math import sqrt
import numpy as np
import os
import cv2
from getpoint import GetPoint

class Tempdiscern():
    def __init__(self,r=8,R=11,E=14,a=255,b=0):
        self.r = r
        self.R = R
        self.E = E
        self.a = a
        self.b = b
        self.gg = GetPoint()
        self.clf1 = self.gg.clf1
        self.clf2 = self.gg.clf2
        self.clf3 = self.gg.clf3
        self.clf4 = self.gg.clf4


        self.p_img = self.point_mask()

    def get_degrees(self):
        self.purple_img = self.purple_degree()
        self.blue_img = self.blue_degree()
        self.black_img = self.black_degree()
        self.white_img = self.white_degree()



    def white_degree(self):
        threshold_1 = 105#105 150
        threshold_2 = 123#123 180
        white_re = np.zeros((self.img.shape[0],self.img.shape[1]))
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                if int(self.img[i, j, 0]) + int(self.img[i, j, 1]) + int(self.img[i, j, 2]) < 560: #600
                    white_re[i, j] = -1
                    continue
                a = pow(int(self.img[i, j, 0]) - int(self.img[i, j, 1]), 2) + pow(int(self.img[i, j, 0]) - int(self.img[i, j, 2]), 2) \
                    + pow(int(self.img[i, j, 1]) - int(self.img[i, j, 2]), 2)
                if (a < threshold_1):
                    white_re[i,j] = 1
                elif (a < threshold_2):#123
                    white_re[i,j] = 0
                else:
                    white_re[i, j] = -1
        #n_img.show("white_degree")
        #print("white_degree is ok")
        return white_re



    def blue_degree(self):
        threshold_1 = 8
        threshold_2 = 15
        blue_re = np.zeros((self.img.shape[0], self.img.shape[1]))
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                if self.img[i, j, 2] < 190 or int(self.img[i,j, 0]) + int(self.img[i,j, 1]) > 320:
                    blue_re[i, j] = -1
                    continue
                a = int(self.img[i,j, 1]) - 1.11*int(self.img[i,j, 0]) - 10.35
                if (a < threshold_1 and self.img[i,j, 2] > 195):
                    blue_re[i, j] = 1
                elif (a < threshold_2 and self.img[i,j, 2] > 190):
                    blue_re[i, j] = 0
                else:
                    blue_re[i, j] = -1
        #n_img.show("blue_degree")
        #print("blue_degree is ok")
        return blue_re

    def black_degree(self):
        threshold_1 = 5
        threshold_2 = 10
        black_re = np.zeros((self.img.shape[0], self.img.shape[1]))
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                if  int(self.img[i, j, 0]) + int(self.img[i, j, 1]) + int(self.img[i, j, 2])> 260:
                    black_re[i, j] = -1
                    continue
                a = int(self.img[i, j, 1]) - 0.617 * int(self.img[i, j, 0]) - 18.47
                if (a < threshold_1):
                    black_re[i, j] = 1
                elif (a < threshold_2):
                    black_re[i, j] = 0
                else:
                    black_re[i, j] = -1
        #n_img.show("black_degree")
        #print("black degree is ok")
        return black_re

    def purple_degree(self):
        threshold_1 = 5
        threshold_2 = 10
        n_img = Image.new("L", (self.img.shape[1], self.img.shape[0]))
        n_pix = n_img.load()
        purple_re = np.zeros((self.img.shape[0], self.img.shape[1]))
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                if self.img[i, j, 2] < 160 or self.img[i, j, 2] > 200:
                    purple_re[i, j] = -1
                    n_pix[j,i] = 0
                    continue
                a = int(self.img[i, j, 1]) - 0.934 * int(self.img[i, j, 0]) + 0.184
                if (a < threshold_1 ):
                    purple_re[i, j] = 1
                    n_pix[j,i] = 255
                elif (a < threshold_2):
                    purple_re[i, j] = 0
                    n_pix[j,i] = 128
                else:
                    purple_re[i, j] = -1
                    n_pix[j,i] = 0
        n_img.show("purple_degree")
        #print("purple degree is ok")

        return purple_re


    def point_mask(self):
        pa = 1
        pb = -1

        center_x = 14
        center_y = 14
        point_re = np.zeros((2 * self.E + 1, 2 * self.E + 1))
        for i in range(2 * self.E + 1):
            for j in range(2 * self.E + 1):
                disqure = pow(i - center_x, 2) + pow(j - center_y, 2)
                if disqure < self.r * self.r:
                    point_re[i,j] = pa
                elif disqure < self.R * self.R:
                    point_re[i, j] = (pb * (disqure - self.r * self.r) + pa * (self.R * self.R - disqure)) / (self.R * self.R - self.r * self.r)
                elif disqure < self.E * self.E:
                    point_re[i, j] = pb
                else:
                    pass
        return point_re

    def likeness(self, center_x, center_y, color):
        x = center_x
        y = center_y
        E = self.E
        if color == "white":
            white_part = self.white_img[x-E:x+E+1, y-E:y+E+1]
            re_np = self.p_img*white_part
        elif color == "blue":
            blue_part = self.blue_img[x - E:x + E + 1, y - E:y + E + 1]
            re_np = self.p_img * blue_part
        elif color == "purple":
            purple_part = self.purple_img[x - E:x + E + 1, y - E:y + E + 1]
            re_np = self.p_img * purple_part
        elif color == "black":
            black_part = self.black_img[x - E:x + E + 1, y - E:y + E + 1]
            re_np = self.p_img * black_part
        else:
            print("parameter color in likeness is wrong")
        # print("    --------------- - - - - -  - - -- -  - - - - - ")
        # print(re_np.shape)
        # print(type(re_np.sum()))
        return re_np.sum()


    def discern(self, img):
        self.img = img#cv2.imread(img)
        print(self.img.shape[0])
        self.img = self.img[60:420, 80:560]
        #cv2.imshow("img", self.img)
        #cv2.waitKey(0)

        #self.get_degrees()
        jmg = self.img.reshape((-1,3))
        pre1 = self.clf1.predict(jmg)
        pre2 = self.clf2.predict(jmg)
        pre3 = self.clf3.predict(jmg)
        pre4 = self.clf4.predict(jmg)
        for pre in pre1, pre2, pre3, pre4:
            pre.resize((self.img.shape[0], self.img.shape[1]))
            #print(255*pre)
        #pre1 = (pre1 + 1)/2
        #pre2 = (pre2 + 1)/2
        #pre3 = (pre3 + 1)/2
        #pre4 = (pre4 + 1)/2

        self.black_img = pre1
        #cv2.imshow("black", 255*self.black_img)
        #cv2.waitKey(0)
        self.blue_img = pre2
        #cv2.imshow("blue", 255*self.blue_img)
        #cv2.waitKey(0)
        self.white_img = pre3
        #cv2.imshow("white", 255*(self.white_img+1)/2)
        #cv2.waitKey(0)
        self.purple_img = pre4
        #cv2.imshow("purple", 255*(self.purple_img+1)/2)
        #cv2.waitKey(0)
        #print(255*self.blue_img)

        # n_img = Image.new("L", self.img.shape)
        # n_pix = n_img.load()
        color_n = [0, 0, 0, 0]
        color_name = ["purple", "blue", "black", "white"]
        for x in range(self.img.shape[0] - 2 * self.E):
            for y in range(self.img.shape[1] - 2 * self.E):
                purple = self.likeness(x + self.E, y + self.E, "purple")
                blue = self.likeness(x + self.E, y + self.E, "blue")
                black = self.likeness(x + self.E, y + self.E, "black")
                white = self.likeness(x + self.E, y + self.E, "white")
                colors = [purple, blue, black, white]
                for i in range(4):
                    if colors[i] > 280:#280
                        color_n[i] += 1
        print(color_n)
        print(color_name[color_n.index(max(color_n))])

        print("            ")


#t = Tempdiscern()
#t.discern('55 (2).png')

'''
white: 111111/17/cam1/50.png, 222222/19/cam1/42.png
blue:  111111/9/cam1/50.png, 222222/12/cam1/52.png
black: black/BING_HEI/WIN_20181128_16_34_38_Pro.jpg, black/BING_HEI/WIN_20181128_16_33_26_Pro.jpg
purple: 111111/2/cam1/54.png 222222/2/cam1/59.png

'''

'''
print(img.shape)
print(pix[391,251])
print(pix[391,268])
print(pix[400,260])
print(pix[391,260])
print(pix[389,256])
print(pix[391,261])
print(pix[397,262])
print(pix[387,263])
print(pix[389,255])
'''
'''
for i in range(img.size[0]):
    for j in range(img.size[1]):
        if(pix[i,j][0]>173 & pix[i,j][0]<200 & pix[i,j][1]>197 & pix[i,j][1]<202 &pix[i,j][2]>199 & pix[i,j][2]<213):
            pix[i,j]=(0,0,0)
'''
#img.show()
#conF = img.filter(ImageFilter.CONTOUR)             ##找轮廓
#conF.show()




