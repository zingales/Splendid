import csv
from pathlib import Path
from collections import defaultdict
import logging

import imageDrawing
from PDFMaker import PdfSize, US_LETTER_IN


from splendid import ResourceType, ResourceCard, VIPCard, ResourceToken, AssetGetter, SplendidSharedAssetts

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


def loadResourceCardsFromCsv(csvFile, sharedImages) -> tuple[list[ResourceCard], list[Exception]]:
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
                cards.append(ResourceCard(produces=generates, requires=requirements,level=cardLevel,victoryPoints=victoryPoints, sharedImages=sharedImages))
            except (KeyError,ValueError) as e:
                customError = BadCSVRow(rowCount, f"{row}", e)
                errors.append(customError)

            rowCount+=1

        return cards, errors

def generateTokenCards(assetGetter:AssetGetter, outputImageFolderPath, sharedImages):

    resourceTokens = list()
    for resourceType in ResourceType:
        if (resourceType == ResourceType.Avatar):
            continue
        image = assetGetter.getResourceImagePath(resourceType)
        sharedImages.loadResourceTypeImage(resourceType, image)
        resourceTokens.append(ResourceToken(resourceType, image))

    avatarTokens = list()
    imagePaths = assetGetter.getAvatarImagesPath()

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


# def generateResourceCards(resourceCards, assetGetter:AssetGetter, outputImageFolderPath, sharedImages):
#     resourceCardBackPath = assetGetter.getResourceCardBackPath()
#     resourceCardBackPaths = imageDrawing.generateResourceCardBacks(outputImageFolderPath,resourceCardBackPath,sharedImages.levelIcon)
#     logging.info(f"Resource Cards Backs Generated")
    
#     resourceTypeToImageList = dict()

#     for type in ResourceType.allButAvatar():
#         resourceTypeToImageList[type] = assetGetter.getResourceCardImagePaths(type)

#     cardsOfTypeProduced = {
#         ResourceType.Air: 0,
#         ResourceType.Water:0, 
#         ResourceType.Earth:0,
#         ResourceType.Fire:0,
#         ResourceType.WhiteLotus:0
#     }
    
#     producedCards = list()
#     for card in resourceCards:
#         try:
#             if card.imagePath is None:
#                 if len(resourceTypeToImageList[card.produces]) > 0:
#                     card.imagePath = resourceTypeToImageList[card.produces].pop()
#                 else:
#                     continue
#             outputPath = outputImageFolderPath / f"{card.produces.name}_{cardsOfTypeProduced[card.produces]}.png"
#             imageDrawing.processResourceCard(card, outputPath, sharedImages)
#             card.renderedFrontImage = outputPath
#             card.renderedBackImage = resourceCardBackPaths[card.level-1]

#             cardsOfTypeProduced[card.produces]+=1
#             producedCards.append(card)
#         except IndexError as e:
#             logging.error(e)


#     logging.info(f"Resource Cards Generated")
#     for resourceType, totalCount in cardsOfTypeProduced.items():
#         logging.info(f"{resourceType.name}: {totalCount}")

#     imageTuples = [(card.renderedFrontImage, card.renderedBackImage) for card in producedCards]

#     return imageTuples


def generateVipCards(vipCards, assetGetter:AssetGetter, outputImageFolderPath, sharedImages):
    vipcardBackImagePathRaw = assetGetter.getVipCardBackImageRaw()
    vipcardBackImagePath = imageDrawing.generateVIPCardBack(outputImageFolderPath, vipcardBackImagePathRaw)
    logging.info(f"VIP card back produced")

    vipImagesPaths = assetGetter.getVipImagePaths()

    vipCardsProduced = 0
    for card in vipCards:
        if card.imagePath is None:
            card.imagePath = vipImagesPaths.pop()
        
        outputPath = outputImageFolderPath / f"VIP_{vipCardsProduced}.png"
        imageDrawing.processVIPCard(card, outputPath, sharedImages)
        card.renderedFrontImage = outputPath
        card.renderedBackImage = vipcardBackImagePath
        vipCardsProduced+=1


    logging.info(f"VIP cards produced: {vipCardsProduced}")

    imageTuples = [(card.renderedFrontImage, card.renderedBackImage) for card in vipCards]

    return imageTuples

def main(outputFolderPath, assetGetter:AssetGetter, resourceCardsCSV, vipCardsCSV):

    outputImageFolderPath = outputFolderPath / "images"
    

    imageDrawing.guaranteeFolder(outputImageFolderPath)

    sharedImages = SplendidSharedAssetts(assetGetter)

    pdfManager = PdfSize(US_LETTER_IN[1], US_LETTER_IN[0])

    # Generate Tokens Pdf
    # tokenTuples = generateTokenCards(assetGetter, outputImageFolderPath, sharedImages)
    # pdfManager.makePDF(tokenTuples, outputFolderPath/"Tokens.pdf" ,(imageDrawing.TOKEN_DIAMETER_IN, imageDrawing.TOKEN_DIAMETER_IN))

    # Generate Resource Pdf
    resourceCards, errors = loadResourceCardsFromCsv(resourceCardsCSV, sharedImages)
    logging.info(f"number of cards {len(resourceCards)}")
    logging.info(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        logging.error(f"{errors}")
    
    imageTuples = generateResourceCards(resourceCards, assetGetter, outputImageFolderPath, sharedImages)
    pdfManager.makePDF(imageTuples, outputFolderPath/"ResourceCards.pdf" ,imageDrawing.RESOURCE_CARD_SIZE_IN)

    # Genereate VIP Pdf
    vipCards, errors = loadVIPCardsFromCsv(vipCardsCSV)    
    logging.info(f"number of Vip cards {len(vipCards)}")
    logging.info(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        logging.error(f"{errors}")

    imageTuples = generateVipCards(vipCards, assetGetter, outputImageFolderPath, sharedImages)
    pdfManager.makePDF(imageTuples, outputFolderPath/"VIPCards.pdf" ,imageDrawing.VIP_CARD_SIZE_IN)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    outputFolderPath = Path("C:\\Users\\G\\code\\splendid\\output")

    assetsPath = Path("assets")
    assetGetter = AssetGetter(assetsPath)

    resourceCardsCSV = assetsPath / "resourceCards.csv"
    vipCardsCSV = assetsPath / "VIPCardsTriple.csv"

    main(outputFolderPath, assetGetter, resourceCardsCSV, vipCardsCSV)