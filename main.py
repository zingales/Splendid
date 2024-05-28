import csv
from pathlib import Path
from collections import defaultdict
import logging

import imageDrawing
from PDFMaker import PdfSize, US_LETTER_IN


import splendid
from splendid import ResourceType, ResourceCard, VIPCard, ResourceToken, AssetGetter, SplendidSharedAssetts,ResourceCardCollection, VipResourceCardCollection, ResourceTokenCardCollection

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


def loadVIPCardsFromCsv(csvFile, sharedImages) -> tuple[list[ResourceCard], list[Exception]]:
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
                cards.append(VIPCard(requires=requirements, victoryPoints=victoryPoints, sharedImages=sharedImages))
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



def generateTokenCards(assetGetter:AssetGetter, sharedImages):
    tokenCards = list()
    avatarImages = assetGetter.getAvatarImagesPath()
    for imagePath in avatarImages:
        tokenCards.append(ResourceToken(ResourceType.Avatar, imagePath, sharedImages))

    for type in ResourceType.allButAvatar():
        imagePath = assetGetter.getResourceImagePath(type)
        for _ in range(7):
            tokenCards.append(ResourceToken(type, imagePath, sharedImages))

    return tokenCards

def assignImagesToResourceCards(resourceCards:list[ResourceCard], assetGetter):

    resourceCardBackPath = assetGetter.getResourceCardBackPath()
    resourceTypeToImageList = dict()

    for type in ResourceType.allButAvatar():
        resourceTypeToImageList[type] = assetGetter.getResourceCardImagePaths(type)

    for card in resourceCards:
        if not card.hasBackgroundImageForFrontOfCard():
            if len(resourceTypeToImageList[card.produces]) > 0:
                card.setBackgroundImageForFrontOfCard(resourceTypeToImageList[card.produces].pop())
            else:
                raise Exception(f"not enough images of type {card.produces} to assign a different one to each Resource Card")
        if not card.hasBackgroundImageForBackOfCard():
            card.setBackgroundImageForBackOfCard(resourceCardBackPath)
    
    return



def assignImagesToVIPCards(vipCards, assetGetter:AssetGetter):
    vipCardBack = assetGetter.getVipCardBackImageRaw()

    vipCardImages = assetGetter.getVipImagePaths()
    for card in vipCards:
        if not card.hasBackgroundImageForFrontOfCard():
            if len(vipCardImages) > 0:
                card.setBackgroundImageForFrontOfCard(vipCardImages.pop())
            else:
                raise Exception(f"not enough VIP images of type to assign a different one to each VIPCard")
        if not card.hasBackgroundImageForBackOfCard():
            card.setBackgroundImageForBackOfCard(vipCardBack)
    
    return

def main(outputFolderPath, assetGetter:AssetGetter, resourceCardsCSV, vipCardsCSV):

    outputImageFolderPath = outputFolderPath / "images"
    

    imageDrawing.guaranteeFolder(outputImageFolderPath)

    sharedImages = SplendidSharedAssetts(assetGetter)

    pdfManager = PdfSize(US_LETTER_IN[1], US_LETTER_IN[0])

    # Generate Resource Pdf
    resourceCards, errors = loadResourceCardsFromCsv(resourceCardsCSV, sharedImages)
    logging.info(f"number of cards {len(resourceCards)}")
    logging.info(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        logging.error(f"{errors}")
    
    assignImagesToResourceCards(resourceCards, assetGetter)
    cardCollectionResourceCards = ResourceCardCollection(splendid.RESOURCE_CARD_SIZE_IN, resourceCards)
    pdfManager.makePDFFromCardCollection(cardCollectionResourceCards, outputFolderPath / "ResourceCards.pdf", outputFolderPath / "images")

    # Genereate VIP Pdf
    vipCards, errors = loadVIPCardsFromCsv(vipCardsCSV, sharedImages)    
    logging.info(f"number of Vip cards {len(vipCards)}")
    logging.info(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        logging.error(f"{errors}")

    assignImagesToVIPCards(vipCards, assetGetter)
    cardCollectionVip = VipResourceCardCollection(splendid.VIP_CARD_SIZE_IN, vipCards)
    pdfManager.makePDFFromCardCollection(cardCollectionVip, outputFolderPath / "VIPCards.pdf", outputFolderPath / "images")

    tokenCards = generateTokenCards(assetGetter, sharedImages)
    cardCollectionTokens = ResourceTokenCardCollection(splendid.TOKEN_DIAMETER_IN, tokenCards)
    pdfManager.makePDFFromCardCollection(cardCollectionTokens, outputFolderPath / "Tokens.pdf", outputFolderPath / "images")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    outputFolderPath = Path("output")

    assetsPath = Path("assets")
    assetGetter = AssetGetter(assetsPath)

    # resourceCardsCSV = assetsPath / "resourceCards.csv"
    resourceCardsCSV = assetsPath / "resourceCardsDebug.csv"
    vipCardsCSV = assetsPath / "VIPCardsTriple.csv"

    main(outputFolderPath, assetGetter, resourceCardsCSV, vipCardsCSV)