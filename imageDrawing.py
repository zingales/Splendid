import logging
from splendid import ResourceCard, ResourceType, VIPCard, ResourceToken

from PIL import Image, ImageOps, ImageFont,  ImageDraw 
from pathlib import Path


PLAYING_CARD_SIZE_IN = (2.5, 3.7)

VIP_CARD_SIZE_IN = (2.5, 2.5)

RESOURCE_CARD_SIZE_IN = (4, 2.25)

OUTPUT_DPI = 150

BORDER_SIZE = 10

TOKEN_DIAMETER_IN = 1.5


# Delicate colors background 
# resourceTypeToPILColor = {
#     ResourceType.Air: (249,239,210), 
#     ResourceType.Earth: (225,252,223), 
#     ResourceType.Fire: (251,233,221), 
#     ResourceType.Water: (215,234,247), 
#     ResourceType.WhiteLotus: "White",
#     # I don't think the below is ever needed tbh. Just including it for completness
#     ResourceType.Avatar: "Black"
# }

resourceTypeToPILColor = {
    ResourceType.Air: (245,202,107), 
    ResourceType.Earth: (155,201,102), 
    ResourceType.Fire: (228,141,113), 
    ResourceType.Water: (96,156,230), 
    ResourceType.WhiteLotus: "White",
    # I don't think the below is ever needed. Just including it for completness
    ResourceType.Avatar: "Black"
}




class SplendidSharedAssetts(object):

    producesSize = (100,100)
    requiresSize = (50,50)
    levelIconSize = (20,20)

    def __init__(self) -> None:
        self.resouceTypeToImage = dict()
        self.levelIcon = None

    def loadResourceTypeImage(self, resourceType:ResourceType, imagePath:Path):
        img = Image.open(imagePath)
        image_produces = img.resize(size=self.producesSize)
        image_requires = img.resize(size=self.requiresSize)
        self.resouceTypeToImage[resourceType] = (image_produces, image_requires)

    def getProducesImage(self, resourceType:ResourceType):
        return self.resouceTypeToImage[resourceType][0]
    
    def getRequiresImage(self, resourceType:ResourceType):
        return self.resouceTypeToImage[resourceType][1]
    
    def loadLevelIcon(self, imagePath):
        img = Image.open(imagePath)
        self.levelIcon = img.resize(size=self.levelIconSize)
        
# def getFont(fontname='arial.ttf', fontsize=50):
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



def processToken(token:ResourceToken, output_path:Path):
    img = Image.open(token.imagePath)
    pixels = int(TOKEN_DIAMETER_IN*OUTPUT_DPI)
    tokenImg = img.resize(size=(pixels,pixels))
    tokenImg.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))

def generateVIPCardBack(outputFolder:Path, imagePath:Path):
    img = Image.open(imagePath)
    card_size = VIP_CARD_SIZE_IN
    output_size = tuple(x*OUTPUT_DPI for x in card_size)
    border_color = "Black"
    cardImage = shrink_image(img, output_size, border_color)
    cardImage = cardImage.transpose(Image.ROTATE_180)
    output_path = outputFolder / "VIPCardBack.png"
    cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))
    return output_path


def processVIPCard(vipCard:VIPCard, output_path:Path, sharedImages:SplendidSharedAssetts):
    img = Image.open(vipCard.imagePath)
    card_size = VIP_CARD_SIZE_IN
    output_size = tuple(x*OUTPUT_DPI for x in card_size)
    border_color = "Black"
    new_image = shrink_image(img, output_size, "White")
    cardImage = add_border(new_image, border_color, border_size=1)


    bg_w, bg_h = cardImage.size

    resourceTypeOrder = [ResourceType.WhiteLotus, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.Air]

    reqW,reqH = sharedImages.requiresSize
    
    numberOfrequirements = len(vipCard.requires)

    interstitialSpaces = ((bg_w - 2*BORDER_SIZE) - (numberOfrequirements*reqW)) // numberOfrequirements
    startingXOffset = BORDER_SIZE + interstitialSpaces//2
    
    xOffset = startingXOffset
    yOffset = (bg_h-BORDER_SIZE-reqH-5)
    for resourceType in resourceTypeOrder:
        if vipCard.requires.get(resourceType, 0) == 0:
            continue

        y = yOffset
        toPaste = sharedImages.getRequiresImage(resourceType)
        cardImage.paste(toPaste, (xOffset,y),mask=toPaste)
        xOffset += (interstitialSpaces+reqW)



    ### Everything requiring a draw object
    draw = ImageDraw.Draw(cardImage)

    # Add Numbers to image
    font = getFont()
    addNumber(draw, vipCard.victoryPoints, (25,25), font)

    font = getFont(fontsize=35)
    # I'm doing here a second time instead of inline with the adding of resource, because I don't know if i can do that. 
    xOffset = startingXOffset+reqW
    for resourceType in resourceTypeOrder:
        resourceCount = vipCard.requires.get(resourceType, 0)
        if resourceCount == 0:
            continue

        y = yOffset
        addNumber(draw, resourceCount, (xOffset,y), font)
        xOffset+= interstitialSpaces+reqW

    cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))


def generateResourceCardBacks(outputFolder:Path, imagePath:Path, iconImg:Image):
    output_size = tuple(x*OUTPUT_DPI for x in RESOURCE_CARD_SIZE_IN)

    border_color = "white"
    cardImage = Image.open(imagePath)
    cardImage = shrink_image(cardImage, output_size, border_color)
    cardImage = add_border(cardImage, "black", 1)

    bg_w, bg_h = cardImage.size

    generatedBackPaths = list()

    for i in range(1,4):
        backImg = cardImage.copy()
        addCardLevel(backImg, i, (20,bg_h//2), iconImg, alignmentHorizontal=False)
        addCardLevel(backImg, i, (bg_w-20-iconImg.size[0],bg_h//2), iconImg, alignmentHorizontal=False)
        backImg = backImg.transpose(Image.ROTATE_180)
        output_path = outputFolder / f"ResourceCard_Back_{i}.png"
        generatedBackPaths.append(output_path)
        backImg.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))

    return generatedBackPaths
    

def processResourceCard(resourceCard:ResourceCard, output_path:Path, sharedImages:SplendidSharedAssetts):
    img = Image.open(resourceCard.imagePath)

    # create background image
    card_size = RESOURCE_CARD_SIZE_IN
    output_size = tuple(x*OUTPUT_DPI for x in card_size)
    border_color = resourceTypeToPILColor[resourceCard.produces]
    new_image = shrink_image(img, output_size, border_color)
    cardImage = add_border(new_image, border_color)
    cardImage = add_border(cardImage, "black", 1)

    # Add produces in the corner
    producesImage = sharedImages.getProducesImage(resourceCard.produces)
    pImg_w, pImg_h = producesImage.size
    bg_w, bg_h = cardImage.size
    offset = ((bg_w - pImg_w)-BORDER_SIZE, BORDER_SIZE)
    cardImage.paste(producesImage, offset, mask=producesImage)

    # Add Requirements across the bottom. 
    # Implicit order
    # WhiteLotus, Water, Earth, Fire, Air
    resourceTypeOrder = [ResourceType.WhiteLotus, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.Air]

    reqW,reqH = sharedImages.requiresSize
    
    interstitialSpaces = ((bg_w - 2*BORDER_SIZE) - (5*reqW)) // 5
    startingXOffset = BORDER_SIZE + interstitialSpaces//2
    
    yOffset = (bg_h-BORDER_SIZE-reqH-5)
    for index, resourceType in enumerate(resourceTypeOrder):
        if resourceCard.requires.get(resourceType, 0) == 0:
            continue

        x = (interstitialSpaces+reqW)*index+startingXOffset
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
        addNumber(draw, resourceCard.victoryPoints, (25,25), font)

    font = getFont(fontsize=35)
    # I'm doing here a second time instead of inline with the adding of resource, because I don't know if i can do that. 
    for index, resourceType in enumerate(resourceTypeOrder):
        resourceCount = resourceCard.requires.get(resourceType, 0)
        if resourceCount == 0:
            continue

        x = (interstitialSpaces+reqW)*index+startingXOffset+reqW
        y = yOffset 
        addNumber(draw, resourceCount, (x,y), font)
    
    cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))


def add_border(img, border_color, border_size=BORDER_SIZE, cropInsteadOfShrink=True):
    x,y = img.size
    
    if cropInsteadOfShrink:
        smaller_image = img.crop(box=(border_size,border_size,x-border_size,y-border_size))
    else:
        smaller_image = None
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

