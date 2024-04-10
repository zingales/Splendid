import csv
from pathlib import Path
from collections import defaultdict

import imageDrawing
from PDFMaker import PdfSize, US_LETTER_IN


from splendid import ResourceType, ResourceCard, VIPCard, ResourceToken

conversionColorToResourceType = {
    'Black': ResourceType.Air,
    'White': ResourceType.WhiteLotus,
    'Blue': ResourceType.Water,
    'Green':ResourceType.Earth,
    'Red':ResourceType.Fire,
    'Gold':ResourceType.Avatar
}


class BadCSVRow(ValueError):
    def __init__(self, csvRowNumber, rowContents, error):            
        super().__init__(f"Bad CSV Row. Row no.{csvRowNumber}, {error}: row contents {rowContents}")

        self.rowNumber = csvRowNumber
        self.previousError = error
        self.rowContents = rowContents


def loadVIPCardsFromCsv(csvFile) -> tuple[list[ResourceCard], list[Exception]]:
    with open(csvFile, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        cards = list()
        errors = list()
        rowCount = 1
        for row in reader:
            try:
                victoryPoints = int(row['Victor Points']) 
                requirements = dict()
                for ogColor, resourceType in conversionColorToResourceType.items():
                    # no resource card requires gold
                    if resourceType == ResourceType.Avatar:
                        continue
                    if row[ogColor] != '':
                        requirements[resourceType] = int(row[ogColor])
                cards.append(VIPCard(requires=requirements, victoryPoints=victoryPoints))
            except (KeyError,ValueError) as e:
                customError = BadCSVRow(rowCount, f"{row}", e)
                errors.append(customError)
            rowCount+=1

    return cards, errors


def loadResourceCardsFromCsv(csvFile) -> tuple[list[ResourceCard], list[Exception]]:
    with open(csvFile, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        cards = list()
        errors = list()
        rowCount = 1
        for row in reader:
            try:
                cardLevel = int(row['Card Level'])
                victoryPoints = 0 if row['VP'] == 0 else int(row['VP']) 
                generates = conversionColorToResourceType[row['Generates']]
                requirements = dict()
                for ogColor, resourceType in conversionColorToResourceType.items():
                    # no resource card requires gold
                    if resourceType == ResourceType.Avatar:
                        continue
                    if row[ogColor] != '':
                        requirements[resourceType] = int(row[ogColor])
                cards.append(ResourceCard(produces=generates, requires=requirements,level=cardLevel,victoryPoints=victoryPoints))
            except (KeyError,ValueError) as e:
                customError = BadCSVRow(rowCount, f"{row}", e)
                errors.append(customError)

            rowCount+=1

        return cards, errors



def loadAllResourceImagePaths(assetFolder:Path):
    ResourceCardFolderName = "Resource Cards Images"    
    AirFolder = "Air Tribe"
    EarthFolder = "Earth Kingdom"
    FireFolder = "Fire Nation"
    WaterFolder = "Water Tribe"
    WhiteLotusFolder = "White Lotus"

    folderNameToResourceType = {
        AirFolder:ResourceType.Air,
        EarthFolder:ResourceType.Earth,
        FireFolder:ResourceType.Fire,
        WaterFolder:ResourceType.Water,
        WhiteLotusFolder:ResourceType.WhiteLotus
    }

    toReturn = defaultdict(list)

    for folderName, resourceType in folderNameToResourceType.items():
        path = assetFolder / ResourceCardFolderName / folderName

        images = Path(path).glob("*.png")
        toReturn[resourceType] = [str(p) for p in images]


    return toReturn

def guaranteeFolder(path:Path):
    path.mkdir(parents=True, exist_ok=True)


def generateTokenCards(assetsPath, outputImageFolderPath, sharedImages):

    resourceTypeToImage = {
        ResourceType.Air: assetsPath/ "Resource Type Images" / "Air.png",
        ResourceType.Water:assetsPath/ "Resource Type Images" / "Water.png",
        ResourceType.Earth:assetsPath/ "Resource Type Images" / "Earth.png",
        ResourceType.Fire:assetsPath/ "Resource Type Images" / "Fire.png",
        ResourceType.WhiteLotus:assetsPath/ "Resource Type Images" / "WhiteLotus.png",
    }

    resourceTokens = list()
    for resourceType, image in resourceTypeToImage.items():
        sharedImages.loadResourceTypeImage(resourceType, image)
        resourceTokens.append(ResourceToken(resourceType, image))

    avatarTokens = list()
    avatarPaths = assetsPath / "Avatar Coins"
    imagePaths = Path(avatarPaths).glob("*.png")
    for imagePath in imagePaths:
        avatarTokens.append(ResourceToken(ResourceType.Avatar, imagePath))


    allDistinctTokens = list()
    allDistinctTokens.extend(avatarTokens)
    allDistinctTokens.extend(resourceTokens)
    tokenCounts = defaultdict(int)
    for token in allDistinctTokens:
        tokenPath = outputImageFolderPath / f"token_{token.resourceType.name}_{tokenCounts[token.resourceType]}.png"
        imageDrawing.processToken(token, tokenPath)
        token.renderedFrontImage = tokenPath
        tokenCounts[token.resourceType]+=1

    
    imageTuples = [(token.renderedFrontImage, None) for token in avatarTokens]

    for token in resourceTokens:
        for _ in range(7):
            # Each resource token has 7 identical multiples
            imageTuples.append((token.renderedFrontImage, None))

    return imageTuples


def generateResourceCards(assetsPath, outputImageFolderPath, sharedImages):
    resourceCardBackPath = assetsPath/ "ResourceCardBack.png"
    resourceCardBackPaths = imageDrawing.generateResourceCardBacks(outputImageFolderPath,resourceCardBackPath,sharedImages.levelIcon)
    print(f"Resource Cards Backs Generated")

    resourceCardsCSV = assetsPath / "resourceCards.csv"
    # resourceCardsCSV = assetsPath / "resourceCards_debug.csv"
    resourceCards,errors = loadResourceCardsFromCsv(resourceCardsCSV)
    print(f"number of cards {len(resourceCards)}")
    print(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        print(f"{errors}")
    
    resourceTypeToImageList = loadAllResourceImagePaths(assetsPath)

    cardsOfTypeProduced = {
        ResourceType.Air: 0,
        ResourceType.Water:0, 
        ResourceType.Earth:0,
        ResourceType.Fire:0,
        ResourceType.WhiteLotus:0
    }
    for card in resourceCards:
        
        try:
            if card.imagePath is None:
                card.imagePath = resourceTypeToImageList[card.produces].pop()

            outputPath = outputImageFolderPath / f"{card.produces.name}_{cardsOfTypeProduced[card.produces]}.png"
            imageDrawing.processResourceCard(card, outputPath, sharedImages)
            card.renderedFrontImage = outputPath
            card.renderedBackImage = resourceCardBackPaths[card.level-1]

            cardsOfTypeProduced[card.produces]+=1
        except IndexError as e:
            print(e)


    print(f"Resource Cards Generated")
    for resourceType, totalCount in cardsOfTypeProduced.items():
        print(f"{resourceType.name}: {totalCount}")

    imageTuples = [(card.renderedFrontImage, card.renderedBackImage) for card in resourceCards]

    return imageTuples


def generateVipCards(assetsPath, outputImageFolderPath, sharedImages):
    vipcardBackImagePathRaw = assetsPath / "VIPCardBack.png"
    vipcardBackImagePath = imageDrawing.generateVIPCardBack(outputImageFolderPath, vipcardBackImagePathRaw)
    print(f"VIP card back produced")

    vipCards, errors = loadVIPCardsFromCsv(assetsPath / "VIPCardsTriple.csv")    
    print(f"number of Vip cards {len(vipCards)}")
    print(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        print(f"{errors}")

    path = assetsPath / "VIP Images"
    images = Path(path).glob("*.png")
    vipImagesPaths = [str(p) for p in images]

    vipCardsProduced = 0
    for card in vipCards:
        if card.imagePath is None:
            card.imagePath = vipImagesPaths.pop()
        
        outputPath = outputImageFolderPath / f"VIP_{vipCardsProduced}.png"
        imageDrawing.processVIPCard(card, outputPath, sharedImages)
        card.renderedFrontImage = outputPath
        card.renderedBackImage = vipcardBackImagePath
        vipCardsProduced+=1


    print(f"VIP cards produced: {vipCardsProduced}")

    imageTuples = [(card.renderedFrontImage, card.renderedBackImage) for card in vipCards]

    return imageTuples

def main(outputFolderPath, assetsPath):

    outputImageFolderPath = outputFolderPath / "images"
    

    guaranteeFolder(outputImageFolderPath)

    #Load resource type images

    sharedImages = imageDrawing.SplendidSharedAssetts()

    sharedImages.loadLevelIcon(assetsPath/ "level_icon.png")

    pdfManager = PdfSize(US_LETTER_IN[1], US_LETTER_IN[0])

    # Generate Tokens Pdf
    # tokenTuples = generateTokenCards(assetsPath, outputImageFolderPath, sharedImages)
    # pdfManager.makePDF(tokenTuples, outputFolderPath/"Tokens.pdf" ,(imageDrawing.TOKEN_DIAMETER_IN, imageDrawing.TOKEN_DIAMETER_IN))

    # Generate Resource Pdf
    imageTuples = generateResourceCards(assetsPath, outputImageFolderPath, sharedImages)
    pdfManager.makePDF(imageTuples, outputFolderPath/"ResourceCards.pdf" ,imageDrawing.RESOURCE_CARD_SIZE_IN)

    # Genereate VIP Pdf
    imageTuples = generateVipCards(assetsPath, outputImageFolderPath, sharedImages)
    pdfManager.makePDF(imageTuples, outputFolderPath/"VIPCards.pdf" ,imageDrawing.VIP_CARD_SIZE_IN)


if __name__ == "__main__":
    outputFolderPath = Path("/Users/gzingales/Downloads/SplendidOutput/v5")
    assetsPath = Path("assets")

    main(outputFolderPath, assetsPath)