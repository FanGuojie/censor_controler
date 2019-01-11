#-*-UTF-8-*-
from PIL import Image
from PIL import ImageFilter
from math import sqrt
import numpy as np
import time
#the image is coped
class Tempdiscern():
    def __init__(self, filepath,r=8,R=11,E=14,a=255,b=0):
        self.r = r
        self.R = R
        self.E = E
        self.a = a
        self.b = b
        t_img = self.loadImage(filepath)
        self.img = t_img.crop([60,60,600,400])
        self.pix = self.img.load()
        self.img.show()

        print("loadimage is ok")
        '''
        print(self.pix[285,261])
        print(self.pix[284, 266])
        print(self.pix[492, 151])
        print(self.pix[176, 280])
        print(self.pix[277, 161])
        print(self.pix[271, 162])
        print(self.pix[167, 179])
        print(self.pix[281, 163])

        print(self.pix[391, 251])
        print(self.pix[391, 268])
        print(self.pix[400, 260])
        print(self.pix[391, 260])
        print(self.pix[389, 256])
        print(self.pix[391, 261])
        print(self.pix[397, 262])
        print(self.pix[387, 263])
        print(self.pix[389, 255])
        '''
        '''
        blue
        print(self.pix[379, 167])
        print(self.pix[375, 170])
        print(self.pix[280, 272])
        print(self.pix[275, 168])
        print(self.pix[488, 162])
        print(self.pix[282, 374])
        print(self.pix[378, 160])
        print(self.pix[493, 365])
        print(self.pix[480, 163])
        print(self.pix[378, 162])
        print(self.pix[376, 163])
        #another png
        print(self.pix[379, 169])
        print(self.pix[276, 272])
        print(self.pix[378, 63])
        print(self.pix[271, 171])
        print(self.pix[266, 66])
        print(self.pix[386, 372])
        print(self.pix[379, 167])
        print(self.pix[274, 174])
        print(self.pix[277, 272])
        '''
        '''
        black
        print(self.pix[408, 32])
        print(self.pix[406, 152])
        print(self.pix[404, 155])
        print(self.pix[401, 148])
        print(self.pix[283, 273])
        print(self.pix[284, 148])
        print(self.pix[404, 272])
        print(self.pix[403, 265])
        print("tu")
        print(self.pix[285, 150])
        print(self.pix[284, 152])
        print(self.pix[407, 154])
        print(self.pix[399, 155])
        print(self.pix[405, 279])
        print(self.pix[281, 273])
        print(self.pix[525, 155])
        '''
        '''
        print(self.pix[277, 269])
        print(self.pix[277, 272])
        print(self.pix[273, 274])
        print(self.pix[279, 270])
        print(self.pix[381, 268])
        print(self.pix[272, 169])
        print(self.pix[381, 263])
        print(self.pix[487, 263])
        print(self.pix[269, 170])
        print("tu")
        print(self.pix[378, 153])
        print(self.pix[380, 154])
        print(self.pix[386, 262])
        print(self.pix[382, 265])
        print(self.pix[262, 45])
        print(self.pix[285, 374])
        print(self.pix[393, 366])
        print(self.pix[490, 143])
        '''


























        self.white_img = self.white_degree()
        self.black_img = self.black_degree()
        self.blue_img = self.blue_degree()
        self.purple_img = self.purple_degree()
        self.p_img = self.point_mask()

    def loadImage(self, filepath):
        img = Image.open(filepath)
        img.show()
        return img

    def white_degree(self):
        threshold_1 = 105#105
        threshold_2 = 123#123
        n_img = Image.new("L", self.img.size)
        n_pix = n_img.load()
        pix = self.img.load()
        white_re = np.zeros((self.img.size[0],self.img.size[1]))
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                if pix[i, j][0]+ pix[i, j][1] +pix[i, j][2] < 600: #640
                    n_pix[i, j] = 0
                    white_re[i, j] = -1
                    continue
                a = pow(pix[i, j][0] - pix[i, j][1], 2) + pow(pix[i, j][0] - pix[i, j][2], 2) \
                    + pow(pix[i, j][1] - pix[i, j][2], 2)
                if (a < threshold_1):
                    n_pix[i, j] = 255
                    white_re[i,j] = 1
                elif (a < threshold_2):#123
                    n_pix[i, j] = 128
                    white_re[i,j] = 0
                else:
                    n_pix[i, j] = 0
                    white_re[i, j] = -1
        n_img.show("white_degree")
        return white_re


    '''
        print(white_re[391,261])
        print(white_re[389, 256])
        print(white_re[391, 251])
        print(white_re[391, 268])
        print(white_re[400, 260])
        print(white_re[391, 260])
        print(white_re[389, 256])
        print(white_re[391, 261])
        print(white_re[397, 262])
        print(white_re[387, 263])
        print(white_re[389, 255])

        print(n_pix[391, 261])
        print(n_pix[389, 256])
        print(n_pix[391, 251])
        print(n_pix[391, 268])
        print(n_pix[400, 260])
        print(n_pix[391, 260])
        print(n_pix[389, 256])
        print(n_pix[391, 261])
        print(n_pix[397, 262])
        print(n_pix[387, 263])
        print(n_pix[389, 255])
    '''

    def blue_degree(self):
        threshold_1 = 8
        threshold_2 = 15
        n_img = Image.new("L", self.img.size)
        n_pix = n_img.load()
        pix = self.img.load()
        blue_re = np.zeros((self.img.size[0], self.img.size[1]))
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                if pix[i, j][2] < 190 or pix[i,j][0] + pix[i,j][1] > 320:
                    n_pix[i, j] = 0
                    blue_re[i, j] = -1
                    continue
                a = pix[i,j][1] - 1.11*pix[i,j][0] - 10.35
                if (a < threshold_1 and pix[i,j][2] > 195):
                    n_pix[i, j] = 255
                    blue_re[i, j] = 1
                elif (a < threshold_2 and pix[i,j][2] > 190):
                    n_pix[i, j] = 128
                    blue_re[i, j] = 0
                else:
                    n_pix[i, j] = 0
                    blue_re[i, j] = -1
        n_img.show("blue_degree")
        return blue_re

    def black_degree(self):
        threshold_1 = 5
        threshold_2 = 10
        n_img = Image.new("L", self.img.size)
        n_pix = n_img.load()
        pix = self.img.load()
        black_re = np.zeros((self.img.size[0], self.img.size[1]))
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                if  pix[i, j][0] + pix[i, j][1] + pix[i, j][2]> 260:
                    n_pix[i, j] = 0
                    black_re[i, j] = -1
                    continue
                a = pix[i, j][1] - 0.617 * pix[i, j][0] - 18.47
                if (a < threshold_1):
                    n_pix[i, j] = 255
                    black_re[i, j] = 1
                elif (a < threshold_2):
                    n_pix[i, j] = 128
                    black_re[i, j] = 0
                else:
                    n_pix[i, j] = 0
                    black_re[i, j] = -1
        n_img.show("black_degree")
        return black_re

    def purple_degree(self):
        threshold_1 = 5
        threshold_2 = 10
        n_img = Image.new("L", self.img.size)
        n_pix = n_img.load()
        pix = self.img.load()
        purple_re = np.zeros((self.img.size[0], self.img.size[1]))
        for i in range(self.img.size[0]):
            for j in range(self.img.size[1]):
                if pix[i, j][2] < 160 or pix[i, j][2] > 200:
                    n_pix[i, j] = 0
                    purple_re[i, j] = -1
                    continue
                a = pix[i, j][1] - 0.934 * pix[i, j][0] + 0.184
                if (a < threshold_1 ):
                    n_pix[i, j] = 255
                    purple_re[i, j] = 1
                elif (a < threshold_2):
                    n_pix[i, j] = 128
                    purple_re[i, j] = 0
                else:
                    n_pix[i, j] = 0
                    purple_re[i, j] = -1
        n_img.show("purple_degree")
        return purple_re


    def point_mask(self):
        pa = 1
        pb = -1
        n_img = Image.new("L", (2 * self.E + 1, 2 * self.E + 1))
        n_pix = n_img.load()
        center_x = 14
        center_y = 14
        point_re = np.zeros((n_img.size[0],n_img.size[1]))
        for i in range(n_img.size[0]):
            for j in range(n_img.size[1]):
                disqure = pow(i - center_x, 2) + pow(j - center_y, 2)
                if disqure < self.r * self.r:
                    n_pix[i, j] = self.a
                    point_re[i,j] = pa
                elif disqure < self.R * self.R:
                    n_pix[i, j] = int((self.b * (disqure - self.r * self.r) + self.a * (self.R * self.R - disqure)) / (self.R * self.R - self.r * self.r))
                    point_re[i, j] = (pb * (disqure - self.r * self.r) + pa * (self.R * self.R - disqure)) / (self.R * self.R - self.r * self.r)
                elif disqure < self.E * self.E:
                    n_pix[i, j] = self.b
                    point_re[i, j] = pb
                else:
                    n_pix[i, j] = 0
        n_img.show("point_mask")
        print("point_mask is ok")
        print(point_re)
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
        # print(re_np.size)
        # print(type(re_np.sum()))
        return re_np.sum()


    def discern(self):
        discern_start = time.time()
        r = 8
        E = 14
        purple_n = 0
        blue_n = 0
        black_n = 0
        white_n = 0
        for x in range(self.img.size[0] - 2 * E):
            for y in range(self.img.size[1] - 2 * E):
                purple  = self.likeness(x + E, y + E, "purple")
                blue = self.likeness(x + E, y + E, "blue")
                black = self.likeness(x + E, y + E, "black")
                white = self.likeness(x + E, y + E, "white")
                if purple > 280:
                    purple_n += 1
                if blue > 280:
                    blue_n += 1
                if black > 280:
                    black_n += 1
                if white > 280:
                    white_n += 1
        re_list = purple_n, blue_n, black_n, white_n
        re = re_list.index(max(re_list))
        if re == 0:
            return "purple"
        elif re ==1:
            return "blue"
        elif re == 2:
            return "black"
        else:
            return "white"

        discern_end = time.time()
        print(discern_end - discern_start)

#t = Tempdiscern("/home/robot/Desktop/opSystemSoftware/55 (2).png")
#t.discern()
'''
white: 111111/17/cam1/50.png, 222222/19/cam1/42.png
blue:  111111/9/cam1/50.png, 222222/12/cam1/52.png
black: black/BING_HEI/WIN_20181128_16_34_38_Pro.jpg, black/BING_HEI/WIN_20181128_16_33_26_Pro.jpg
purple: 111111/2/cam1/54.png 222222/2/cam1/59.png

'''

'''
print(img.size)
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




