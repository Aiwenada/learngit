# image.py

__author__ = 'zgy'

from PIL import Image
from pylab import *
from ctypes import *

import os
import threading
import time

class ImageClean:
    def __init__(self, picture_path, new_picture_path):
        self.picture_path = picture_path
        self.new_picture_path = new_picture_path

        if not os.path.isdir(self.new_picture_path):
            os.makedirs(self.new_picture_path)

    def clean_logo(self, picture_name):
        img = Image.open(self.picture_path + picture_name)
        region = img.crop((0, 0, 3, 3))

        x_rang = range(10, 1910)
        y_rang = range(10, 950)

        try:
            for x in x_rang:
                for y in y_rang:
                    if(img.getpixel((x,y)) == 0):
                        if(img.getpixel((x+2,y-2)) == 255 and img.getpixel((x+2,y+2)) == 255 and
                                   img.getpixel((x-2,y-2)) == 255 and img.getpixel((x-2,y+2)) == 255):
                            if(img.getpixel((x-2,y)) == 255 and img.getpixel((x,y-2)) == 255):
                                if(img.getpixel((x,y+2)) == 255):
                                    if(img.getpixel((x+3,y)) == 255 and img.getpixel((x+3,y-1)) == 255 and
                                               img.getpixel((x+3,y+1)) == 255):
                                        img.paste(region,(x-1,y-1,x+2,y+2))
                                        #print('X [%s] Y[%s]' % (x, y))
                                else:
                                    if(img.getpixel((x,y+3)) == 255 and img.getpixel((x-1,y+3)) == 255 and
                                               img.getpixel((x+1,y+3)) == 255):
                                        img.paste(region,(x-1,y-1,x+2,y+2))
                                        #print('X [%s] Y[%s]' % (x, y))
            img.save(self.new_picture_path + picture_name)
        except IOError:
            print("cannot convert")

    def read_picture_name(self, file_list):
        dir = self.picture_path
        for f in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, f)):
                file_list.append(f)
            if os.path.isdir(os.path.join(dir, f)):
                print("Exist Directory: " + f)
        return file_list


class myThread (threading.Thread):
    def __init__(self, threadID, arg):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.arg = arg
    def run(self):
        clean_logo(self.arg)

def clean_logo(Picturename):
    img = Image.open( "F:\\WorkSpace\\IMGE\\IMGE\\" + Picturename)
    region = img.crop((0,0,3,3))

    x_rang = range(10,1910)
    y_rang = range(10,950)

    try:
        for x in x_rang:
            for y in y_rang:
                if( img.getpixel((x,y)) == 0):
                    if( img.getpixel((x-2,y)) == 255 and img.getpixel((x,y+2)) == 255 and
                               img.getpixel((x+2,y)) == 255 and img.getpixel((x,y-2)) == 255 and
                               img.getpixel((x+2,y-2)) == 255):
                        if(img.getpixel((x-7,y)) == 0):
                            continue
                        else:
                            img.paste(region,(x-1,y-1,x+2,y+2))
                            #print('X [%s] Y[%s]' % (x,y))
                            continue

        img.save("F:\\WorkSpace\\IMGE\\IMGE\\new\\"+Picturename)
    except IOError:
        print("cannot convert")

if __name__ == '__main__':
    DoImageClean = ImageClean("F:\\WorkSpace\\IMGE\\IMGE\\","F:\\WorkSpace\\IMGE\\IMGE\\new\\")
    List = DoImageClean.read_picture_name([])

    if(List is not None and len(List) > 0 ):
        print("File List = ", List)
        startTime = time.strftime("%Y-%m-%d %H:%M:%S"), time.localtime(time.time())
        for e in List:
            print("File=[%s]" % e)
            #i = i+1
            #thread = myThread(i,e)
            #thread.start()
            DoImageClean.clean_logo(e)
        endTime = time.strftime("%Y-%m-%d %H:%M:%S"), time.localtime(time.time())
        print("Start Time = [%s]" % startTime[0])
        print("End Time = [%s]" % endTime[0])
    else:
        print('There is nothing in the fold!')

    #windll.shell32.folderItem.ExtendedProperty("Title")
