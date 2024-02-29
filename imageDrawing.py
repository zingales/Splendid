from splendid import ResourceCard, ResourceType

from PIL import Image, ImageOps, ImageFont,  ImageDraw 
from pathlib import Path


PLAYING_CARD_SIZE_IN = (2.5, 3.7)

OUTPUT_DPI = 150


resourceTypeToPILColor = {
    ResourceType.Air: "Gold", 
    ResourceType.Earth: "Green", 
    ResourceType.Fire: "Red", 
    ResourceType.Water: "Blue", 
    ResourceType.WhiteLotus: "White",
    # I don't think the below is ever needed tbh. Just including it for completness
    ResourceType.Avatar: "Black"
}




def processResourceCard(resourceCard:ResourceCard, output_path:Path):
    img = Image.open(resourceCard.imagePath)

    card_size = reversed(PLAYING_CARD_SIZE_IN)
    output_size = tuple(x*OUTPUT_DPI for x in card_size)
    border_color = resourceTypeToPILColor[resourceCard.produces]
    new_image = shrink_image(img, output_size, border_color)
    new_image = add_border(new_image, border_color)

    new_image.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))


def add_border(img, border_color):
    x,y = img.size
    
    smaller_image = img.crop(box=(10,10,x-10,y-10))
    return ImageOps.expand(smaller_image,  10, fill = border_color)

def shrink_image(img:Image, new_size_pixels:tuple[int, int], fill:str):
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

