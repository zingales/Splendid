import csv
from pathlib import Path
from collections import defaultdict

import imageDrawing
import tempfile


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

def main():

    outputFolderPath = Path("/Users/gzingales/Downloads/SplendidOutput/v4")
    outputImageFolderPath = outputFolderPath / "images"
    assetsPath = Path("assets")


    guaranteeFolder(outputImageFolderPath)

    #Load resource type images

    sharedImages = imageDrawing.SplendidSharedAssetts()

    sharedImages.loadLevelIcon(assetsPath/ "level_icon.png")

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

    avatarPaths = assetsPath / "Avatar Coins"
    imagePaths = Path(avatarPaths).glob("*.png")
    for imagePath in imagePaths:
        resourceTokens.append(ResourceToken(ResourceType.Avatar, imagePath))


    tokenCounts = defaultdict(int)
    for token in resourceTokens:
        tokenPath = outputImageFolderPath / f"token_{token.resourceType.name}_{tokenCounts[token.resourceType]}.png"
        imageDrawing.processToken(token, tokenPath)
        tokenCounts[token.resourceType]+=1

    resourceCardsCSV = assetsPath / "resourceCards.csv"
    # resourceCardsCSV = assetsPath / "resourceCards_debug.csv"
    resourceCards,errors = loadResourceCardsFromCsv(resourceCardsCSV)
    print(f"number of cards {len(resourceCards)}")
    print(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        print(f"{errors}")
    
    resourceTypeToImageList = loadAllResourceImagePaths(assetsPath)

    # assign an image for each card

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

            cardsOfTypeProduced[card.produces]+=1
        except IndexError as e:
            print(e)


    print(f"Resource Cards Generated")
    for resourceType, totalCount in cardsOfTypeProduced.items():
        print(f"{resourceType.name}: {totalCount}")


    # Load VIP cards
        
    vipCards, errors = loadVIPCardsFromCsv(assetsPath / "VIPCards.csv")
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
        vipCardsProduced+=1


    print(f"VIP cards produced: {vipCardsProduced}")



if __name__ == "__main__":
    main()