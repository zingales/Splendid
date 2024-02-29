from splendid import ResourceCard, ResourceType

from PIL import Image, ImageOps, ImageFont,  ImageDraw 
from pathlib import Path


PLAYING_CARD_SIZE_IN = (2.5, 3.7)

OUTPUT_DPI = 150

BORDER_SIZE = 10


resourceTypeToPILColor = {
    ResourceType.Air: "Gold", 
    ResourceType.Earth: "Green", 
    ResourceType.Fire: "Red", 
    ResourceType.Water: "Blue", 
    ResourceType.WhiteLotus: "White",
    # I don't think the below is ever needed tbh. Just including it for completness
    ResourceType.Avatar: "Black"
}


class SplendidSharedAssetts(object):

    producesSize = (100,100)
    requiresSize = (50,50)
    levelIconSize = (20,20)

    def __init__(self) -> None:
        self.resouceTypeToImage = dict()
        self.levelIcon = None

    def saveResourceTypeImage(self, resourceType:ResourceType, imagePath:Path):
        img = Image.open(imagePath)
        image_produces = img.resize(size=self.producesSize)
        image_requires = img.resize(size=self.requiresSize)
        self.resouceTypeToImage[resourceType] = (image_produces, image_requires)

    def getProducesImage(self, resourceType:ResourceType):
        return self.resouceTypeToImage[resourceType][0]
    
    def getRequiresImage(self, resourceType:ResourceType):
        return self.resouceTypeToImage[resourceType][1]
    
    def saveLevelIcon(self, imagePath):
        img = Image.open(imagePath)
        self.levelIcon = img.resize(size=self.levelIconSize)
        



def getFont(fontname='Keyboard.ttf', fontsize=50):
    return ImageFont.truetype(fontname, fontsize)

def addNumber(draw:ImageDraw, number:int, centeredAt:tuple[int,int], font):

    centerX, centerY = centeredAt
    text = str(number)
    _, _, w, h = draw.textbbox(xy= (0, 0), text=text, font=font)

    # loc = (((centerX-w)//2)+centerX, ((centerY-h)//2)+centerY)
    loc = centeredAt
    draw.text(loc,text,fill='white', font=font, stroke_width=2, stroke_fill='black')


def addCardLevel(image, number:int, centeredAt:tuple[int,int], icon:Image):
    centerX, centerY = centeredAt
    x, y = icon.size

    startX = centerX - (number*x)//2 
    for i in range(number):
        image.paste(icon, (startX+(x*i),centerY),mask=icon)



def processResourceCard(resourceCard:ResourceCard, output_path:Path, sharedImages:SplendidSharedAssetts):
    img = Image.open(resourceCard.imagePath)


    # create background image
    card_size = reversed(PLAYING_CARD_SIZE_IN)
    output_size = tuple(x*OUTPUT_DPI for x in card_size)
    border_color = resourceTypeToPILColor[resourceCard.produces]
    new_image = shrink_image(img, output_size, border_color)
    cardImage = add_border(new_image, border_color)

    # Add produces in the corner
    producesImage = sharedImages.getProducesImage(resourceCard.produces)
    img_w, img_h = producesImage.size
    bg_w, bg_h = cardImage.size
    offset = ((bg_w - img_w)-BORDER_SIZE, BORDER_SIZE)
    cardImage.paste(producesImage, offset, mask=producesImage)

    # Add Requirements across the bottom. 
    # Implicit order
    # WhiteLotus, Water, Earth, Fire, Air
    resourceTypeOrder = [ResourceType.WhiteLotus, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.Air]

    xOffsetMultiple = (bg_w - 2*BORDER_SIZE) // 5
    startingXOffset = BORDER_SIZE
    yOffset = (bg_h-BORDER_SIZE-img_h)
    for index, resourceType in enumerate(resourceTypeOrder):
        if resourceCard.requires.get(resourceType, 0) == 0:
            continue

        x = xOffsetMultiple*index+startingXOffset
        y = yOffset
        toPaste = sharedImages.getRequiresImage(resourceType)
        cardImage.paste(toPaste, (x,y),mask=toPaste)


    # Add card level icon(s)
    addCardLevel(cardImage, resourceCard.level, (bg_w//2,20), sharedImages.levelIcon)


    ### Everything requiring a draw object
    draw = ImageDraw.Draw(cardImage)

    # Add Numbers to image
    font = getFont()
    if resourceCard.victoryPoints != 0:
        addNumber(draw, resourceCard.victoryPoints, (20,20), font)

    # I'm doing here a second time instead of inline with the adding of resource, because I don't know if i can do that. 
    for index, resourceType in enumerate(resourceTypeOrder):
        resourceCount = resourceCard.requires.get(resourceType, 0)
        if resourceCount == 0:
            continue

        # x = xOffsetMultiple*(index+0.5)+startingXOffset
        # y = yOffset + (img_h//2)
        x = xOffsetMultiple*index+startingXOffset
        y = yOffset
        addNumber(draw, resourceCount, (x,y), font)
    
    cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))


def add_border(img, border_color):
    x,y = img.size
    
    smaller_image = img.crop(box=(BORDER_SIZE,BORDER_SIZE,x-BORDER_SIZE,y-BORDER_SIZE))
    return ImageOps.expand(smaller_image,  BORDER_SIZE, fill = border_color)

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

