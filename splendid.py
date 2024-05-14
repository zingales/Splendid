from pathlib import Path
from enum import Enum
from typing import Dict, Tuple
from imageDrawing import *

from PDFMaker import Card, CardCollection, POINTS_PER_IN

class ResourceType(Enum):
    WhiteLotus=1
    Water=2
    Earth=3
    Fire=4
    Air=5
    Avatar=6

    def __repr__(self):
        return f'{ResourceType}:{self.name}'
    
    @classmethod
    def allButAvatar(cls):
        return [ResourceType.Air, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.WhiteLotus]
    
resourceTypeOrder = [ResourceType.WhiteLotus, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.Air]

class ResourceToken(object):
    resourceType:ResourceType
    imagePath: Path
    renderedFrontImage:Path 

    def __init__(self, resourceType:ResourceType, imagePath=None) -> None:
        self.resourceType = resourceType
        self.imagePath = imagePath
        self.renderedFrontImage = None

class VIPCard(Card):
    requires:Dict[ResourceType,int]
    victoryPoints:int
    backgroundFront: Path
    backgroundBack: Path

    def __init__(self, requires:Dict[ResourceType,int], victoryPoints:int, sharedImages:'SplendidSharedAssetts') -> None:
        self.requires = requires
        self.victoryPoints = victoryPoints
        self.sharedImages = sharedImages
        self.backgroundFront = None
        self.backgroundBack = None
        

    def __repr__(self) -> str:
        resrouceStrings = list() 
        for resource, count in self.requires.items():
            if count == 0:
                continue
            resrouceStrings.append(f"{resource}: {count}")
        return f"Splendid.VIPCard(VP: {self.victoryPoints}, requires:[{', '.join(resrouceStrings)}], imagePath: {self.imagePath}"
    
    def hasBackgroundImageForFrontOfCard(self):
        return self.backgroundFront is not None
    
    def hasBackgroundImageForBackOfCard(self):
        return self.backgroundBack is not None

    def setBackgroundImageForFrontOfCard(self, path:Path):
        self.backgroundFront = path

    def setBackgroundImageForBackOfCard(self, path:Path):
        self.backgroundBack = path

    # cardImage = cardImage.transpose(Image.ROTATE_180)
    def getBackOfCardPoints(self,  size_in_pts: Tuple[int, int], output_path:Path) -> None:
        img = Image.open(self.backgroundBack)
        output_size = tuple(x//POINTS_PER_IN*OUTPUT_DPI for x in size_in_pts)
        border_color = "Black"
        cardImage = shrink_image(img, output_size, border_color)
        cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))
        return output_path
    

    def getFrontOfCardPoints(self, size_in_pts: Tuple[int, int], output_path:Path):
        img = Image.open(self.backgroundFront)
        card_size = size_in_pts
        output_size = tuple(x//POINTS_PER_IN*OUTPUT_DPI for x in card_size)
        border_color = "Black"
        new_image = shrink_image(img, output_size, "White")
        cardImage = add_border(new_image, border_color, border_size=1)


        bg_w, bg_h = cardImage.size

        

        reqW,reqH = self.sharedImages.requiresSize
        
        numberOfrequirements = len(self.requires)

        interstitialSpaces = ((bg_w - 2*BORDER_SIZE) - (numberOfrequirements*reqW)) // numberOfrequirements
        startingXOffset = BORDER_SIZE + interstitialSpaces//2
        
        xOffset = startingXOffset
        yOffset = (bg_h-BORDER_SIZE-reqH-5)
        for resourceType in resourceTypeOrder:
            if self.requires.get(resourceType, 0) == 0:
                continue

            y = yOffset
            toPaste = self.sharedImages.getRequiresImage(resourceType)
            cardImage.paste(toPaste, (xOffset,y),mask=toPaste)
            xOffset += (interstitialSpaces+reqW)



        ### Everything requiring a draw object
        draw = ImageDraw.Draw(cardImage)

        # Add Numbers to image
        font = getFont()
        addNumber(draw, self.victoryPoints, (25,25), font)

        font = getFont(fontsize=35)
        # I'm doing here a second time instead of inline with the adding of resource, because I don't know if i can do that. 
        xOffset = startingXOffset+reqW
        for resourceType in resourceTypeOrder:
            resourceCount = self.requires.get(resourceType, 0)
            if resourceCount == 0:
                continue

            y = yOffset
            addNumber(draw, resourceCount, (xOffset,y), font)
            xOffset+= interstitialSpaces+reqW

        cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))

class ResourceCard(Card):
    produces:ResourceType
    requires:Dict[ResourceType,int]
    victoryPoints:int
    level:int

    def __init__(self, produces:ResourceType, requires:Dict[ResourceType,int], level:int, victoryPoints:int, sharedImages:'SplendidSharedAssetts') -> None:
        self.produces = produces
        self.requires = requires
        self.victoryPoints = victoryPoints
        self.level = level
        self.sharedImages = sharedImages
        self.backgroundFront = None
        self.backgroundBack = None
        self.cardBackPerLevel = dict()


    def __repr__(self) -> str:
        resrouceStrings = list() 
        for resource, count in self.requires.items():
            if count == 0:
                continue
            resrouceStrings.append(f"{resource}: {count}")
        return f"Splendid.ResourceCard(level: {self.level}, produces: {self.produces}, VP: {self.victoryPoints}, requires:[{', '.join(resrouceStrings)}], imagePath: {self.imagePath}"
    
    def __str__(self) -> str:
        return self.__repr__()
        
    def hasBackgroundImageForFrontOfCard(self):
        return self.backgroundFront is not None
    
    def hasBackgroundImageForBackOfCard(self):
        return self.backgroundBack is not None

    def setBackgroundImageForFrontOfCard(self, path:Path):
        self.backgroundFront = path

    def setBackgroundImageForBackOfCard(self, path:Path):
        self.backgroundBack = path


    def getBackOfCardPoints(self, size_in_pts: Tuple[int, int], output_path:Path) -> Image:
        output_size = tuple(x//POINTS_PER_IN *OUTPUT_DPI for x in size_in_pts)

        border_color = "white"
        cardImage = Image.open(self.backgroundBack)
        cardImage = shrink_image(cardImage, output_size, border_color)
        cardImage = add_border(cardImage, "black", 1)

        bg_w, bg_h = cardImage.size

        generatedBackPaths = dict()
        iconImg = self.sharedImages.getLevelIcon()
        i = self.level

        backImg = cardImage.copy()
        addCardLevel(backImg, i, (20,bg_h//2), iconImg, alignmentHorizontal=False)
        addCardLevel(backImg, i, (bg_w-20-iconImg.size[0],bg_h//2), iconImg, alignmentHorizontal=False)
        backImg = backImg.transpose(Image.ROTATE_180)
        generatedBackPaths[i] = output_path
        backImg.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))
        return backImg
    
    def getFrontOfCardPoints(self, size_in_pts: Tuple[int, int], output_path:Path):
        # def processResourceCard(resourceCard:ResourceCard, output_path:Path, sharedImages:SplendidSharedAssetts):
        img = Image.open(self.backgroundFront)

        # create background image
        output_size = tuple(x//POINTS_PER_IN*OUTPUT_DPI for x in size_in_pts)
        border_color = resourceTypeToPILColor[self.produces]
        new_image = shrink_image(img, output_size, border_color)
        cardImage = add_border(new_image, border_color)
        cardImage = add_border(cardImage, "black", 1)

        # Add produces in the corner
        producesImage = self.sharedImages.getProducesImage(self.produces)
        pImg_w, pImg_h = producesImage.size
        bg_w, bg_h = cardImage.size
        offset = ((bg_w - pImg_w)-BORDER_SIZE, BORDER_SIZE)
        cardImage.paste(producesImage, offset, mask=producesImage)

        # Add Requirements across the bottom. 
        # Implicit order
        # WhiteLotus, Water, Earth, Fire, Air
        resourceTypeOrder = [ResourceType.WhiteLotus, ResourceType.Water, ResourceType.Earth, ResourceType.Fire, ResourceType.Air]

        reqW,reqH = self.sharedImages.requiresSize
        
        interstitialSpaces = ((bg_w - 2*BORDER_SIZE) - (5*reqW)) // 5
        startingXOffset = BORDER_SIZE + interstitialSpaces//2
        
        yOffset = (bg_h-BORDER_SIZE-reqH-5)
        for index, resourceType in enumerate(resourceTypeOrder):
            if self.requires.get(resourceType, 0) == 0:
                continue

            x = (interstitialSpaces+reqW)*index+startingXOffset
            y = yOffset
            toPaste = self.sharedImages.getRequiresImage(resourceType)
            cardImage.paste(toPaste, (x,y),mask=toPaste)


        # Add card level icon(s)
        addCardLevel(cardImage, self.level, (bg_w//2,20), self.sharedImages.getLevelIcon())


        ### Everything requiring a draw object
        draw = ImageDraw.Draw(cardImage)

        # Add Numbers to image
        font = getFont()
        if self.victoryPoints != 0:
            addNumber(draw, self.victoryPoints, (25,25), font)

        font = getFont(fontsize=35)
        # I'm doing here a second time instead of inline with the adding of resource, because I don't know if i can do that. 
        for index, resourceType in enumerate(resourceTypeOrder):
            resourceCount = self.requires.get(resourceType, 0)
            if resourceCount == 0:
                continue

            x = (interstitialSpaces+reqW)*index+startingXOffset+reqW
            y = yOffset 
            addNumber(draw, resourceCount, (x,y), font)
        
        cardImage.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))
        return cardImage
        


class ResourceCardCollection(CardCollection):

    # Handles caching as the back of cards are more or less the same. 
    def getAllImagesAsTuples(self, cardSizeInInches, imageOutputPath:Path):
        imageCache = dict()
        cardTuples = list()
        count = 0
        for card in self.cards:
            assert isinstance(card, ResourceCard)
            frontPath = imageOutputPath / f"ResourceCard_{count:2}_{card.produces}.png"
            front = card.getFrontOfCardInches(cardSizeInInches, frontPath)
            backPath = imageOutputPath / f"ResourceCardBack_{card.level}.png"
            if card.level not in imageCache:
                imageCache[card.level] = card.getBackOfCardInches(cardSizeInInches, backPath)
            cardTuples.append((frontPath,backPath))
            count += 1
            
        return cardTuples


class VipResourceCardCollection(CardCollection):

    def getAllImagesAsTuples(self, cardSizeInInches, imageOutputPath:Path):
        backPath = None
        cardTuples = list()
        count = 0
        for card in self.cards:
            assert isinstance(card, VIPCard)
            frontPath = imageOutputPath / f"VIP_Card_{count:2}.png"
            card.getFrontOfCardInches(cardSizeInInches, frontPath)
            if backPath is None:
                backPath = imageOutputPath / f"VIP_CardBack.png"
                card.getBackOfCardInches(cardSizeInInches, backPath)
            cardTuples.append((frontPath,backPath))
            count += 1
            
        return cardTuples





PLAYING_CARD_SIZE_IN = (2.5, 3.7)



RESOURCE_CARD_SIZE_IN = (4, 2.25)
VIP_CARD_SIZE_IN = (2.5, 2.5)

OUTPUT_DPI = 150

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



class AssetGetter(object):

    def __init__(self, assetsPath:Path) -> None:
        self.assetsPath = assetsPath
        resourceTypeFolder = "Resource Type Images"
        self.resourceTypeToImage = {
            ResourceType.Air: assetsPath/ resourceTypeFolder / "Air.png",
            ResourceType.Water:assetsPath/ resourceTypeFolder / "Water.png",
            ResourceType.Earth:assetsPath/ resourceTypeFolder / "Earth.png",
            ResourceType.Fire:assetsPath/ resourceTypeFolder / "Fire.png",
            ResourceType.WhiteLotus:assetsPath/ resourceTypeFolder / "WhiteLotus.png",
        }

        resourceCardFolder = "Resource Cards Images"
        self.resourceTypeToResourceCardFolder = {
            ResourceType.Air: assetsPath/ resourceCardFolder / "Air Nomads",
            ResourceType.Water:assetsPath/ resourceCardFolder / "Water Tribe",
            ResourceType.Earth:assetsPath/ resourceCardFolder / "Earth Kingdom",
            ResourceType.Fire:assetsPath/ resourceCardFolder / "Fire Nation",
            ResourceType.WhiteLotus:assetsPath/ resourceCardFolder / "White Lotus",
        }

    def getAvatarImagesPath(self) -> Path:
        path = self.assetsPath / "Avatar Coins"
        return path.glob("*.png")
    
    def getResourceImagePath(self, resourceType: ResourceType) -> Path:
        return self.resourceTypeToImage[resourceType]

    def getLevelIcon(self):
        return self.assetsPath / "level_icon.png"
        

    def getResourceCardBackPath(self):
        return self.assetsPath/ "ResourceCardBack.png"
    

    def getResourceCardImagePaths(self, resourceType: ResourceType) -> list[Path]:
        path = self.resourceTypeToResourceCardFolder[resourceType]
        images = Path(path).glob("*.png")
        return list(images)
    
    def getVipCardBackImageRaw(self):
        return self.assetsPath / "VIPCardBack.png"
    
    def getVipImagePaths(self):
        path = self.assetsPath / "VIP Images"
        images = Path(path).glob("*.png")
        return list(images)


class SplendidSharedAssetts(object):

    producesSize = (100,100)
    requiresSize = (50,50)
    levelIconSize = (20,20)
    producesImages: Dict[ResourceType, Image.Image]
    requiresImages: Dict[ResourceType, Image.Image]

    def __init__(self, assetGetter:AssetGetter) -> None:
        self.assetGetter = assetGetter
        self.producesImages = dict()
        self.requiresImages = dict()
        self.levelImage = None

    def _loadResourceTypeImage(self, resourceType:ResourceType):
        img = Image.open(self.assetGetter.getResourceImagePath(resourceType))
        image_produces = img.resize(size=self.producesSize)
        image_requires = img.resize(size=self.requiresSize)
        self.producesImages[resourceType] = image_produces
        self.requiresImages[resourceType] = image_requires

    def getProducesImage(self, resourceType:ResourceType):
        if resourceType not in self.producesImages:
            self._loadResourceTypeImage(resourceType)
        return self.producesImages[resourceType]
    
    def getRequiresImage(self, resourceType:ResourceType):
        if resourceType not in self.requiresImages:
            self._loadResourceTypeImage(resourceType)
        return self.requiresImages[resourceType]
    
    def getLevelIcon(self):
        if self.levelImage is None:
            img = Image.open(self.assetGetter.getLevelIcon())
            self.levelImage =  img.resize(size=self.levelIconSize)
        return self.levelImage

def processToken(token:ResourceToken, output_path:Path):
    img = Image.open(token.imagePath)
    pixels = int(TOKEN_DIAMETER_IN*OUTPUT_DPI)
    tokenImg = img.resize(size=(pixels,pixels))
    tokenImg.save(output_path, dpi=(OUTPUT_DPI,OUTPUT_DPI))


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
