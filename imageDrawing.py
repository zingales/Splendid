import logging
from PIL import Image, ImageOps, ImageFont,  ImageDraw 
from pathlib import Path

BORDER_SIZE = 10

def guaranteeFolder(path:Path):
    path.mkdir(parents=True, exist_ok=True)


def getFont(fontname='Herculanum.ttf', fontsize=50):
    try:
        return ImageFont.truetype(fontname, fontsize)
    except OSError:
        logging.debug(f"could not find font {fontname}. Loading default instead")
        return ImageFont.load_default(size=fontsize)

    return 

def addNumber(draw:ImageDraw, number:int, centeredAt:tuple[int,int], font):

    centerX, centerY = centeredAt
    text = str(number)
    _, _, w, h = draw.textbbox(xy= (0, 0), text=text, font=font)

    
    loc = (centerX-(w//2), centerY-(h//2))
    if loc[0] < 0 or loc[1] < 0:
        raise ValueError("Center at postion is smaller than the width of the number")
    draw.text(loc,text,fill='white', font=font, stroke_width=2, stroke_fill='black')

def symmetricalCrop(img, shrinkX, shrinkY):
    img_size_x, img_size_y = img.size
    return img.crop(box=(shrinkX,shrinkY,img_size_x-shrinkX,img_size_y-shrinkY))

def addCardLevel(image, number:int, centeredAt:tuple[int,int], icon:Image, alignmentHorizontal=True):
    centerX, centerY = centeredAt
    x, y = icon.size

    if alignmentHorizontal:
        startX = centerX - (number*x)//2 
        for i in range(number):
            image.paste(icon, (startX+(x*i),centerY),mask=icon)
    else:
        startY = centerY - (number*y)//2 
        for i in range(number):
            image.paste(icon, (centerX,startY+ (y*i)),mask=icon)



def add_border(img, border_color, border_size=BORDER_SIZE, cropInsteadOfShrink=True):
    x,y = img.size
    
    if cropInsteadOfShrink:
        smaller_image = img.crop(box=(border_size,border_size,x-border_size,y-border_size))
    else:
        smaller_image = img.resize(size=(int(x-(2*border_size)),int(y-(2*border_size))))
    return ImageOps.expand(smaller_image,  border_size, fill = border_color)

def shrink_image(img:Image, new_size_pixels:tuple[int, int], fill):
    desired_x, desired_y = new_size_pixels

    img_size_y, img_size_x = img.size
    
    ratioed_x = (img_size_y/img_size_x) * desired_y
    ratioed_y = (img_size_x/img_size_y) * desired_x

    x = desired_x
    y = desired_y

    fill_required = False
    if ratioed_x > desired_x:
        y = ratioed_y
        fill_required = True

    if ratioed_y > desired_y:
        x = ratioed_x
        fill_required = True

    
    new_image = img.resize(size=(int(x),int(y)))

    if fill_required:
        x_border = int((desired_x-x)/2)
        y_border = int((desired_y-y)/2)
        new_image = ImageOps.expand(new_image, border=(x_border,y_border), fill=fill)
    
    return new_image

