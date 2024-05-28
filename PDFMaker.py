from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pagesizes
from pathlib import Path
from typing import Tuple
from typing import Dict, Tuple, List

OUTPUT_DPI = 150
POINTS_PER_IN = 72
MARGIN_IN_PTS = 24

US_LETTER_IN = (8.5, 11)

class Card(object):

    sizeInInches : Tuple[float, float]

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return "A Card"
        

    def getFrontOfCardInches(self, size_in_inches: Tuple[float, float], output_path:Path) -> None:
        return self.getFrontOfCardPoints(size_in_pts=(x*POINTS_PER_IN for x in size_in_inches), output_path=output_path)
    
    
    def getBackOfCardInches(self, size_in_inches: Tuple[float, float], output_path:Path) -> None:
        return self.getBackOfCardPoints([x*POINTS_PER_IN for x in size_in_inches], output_path)
    
    def getFrontOfCardPoints(self, size_in_pts: Tuple[int, int], output_path:Path) -> None:
        raise NotImplementedError("Must be implemented by the child class")
    
    def getBackOfCardPoints(self, size_in_pts: Tuple[int, int], output_path:Path) -> None:
        raise NotImplementedError("Must be implemented by the child class")


class CardCollection(object):

    cards : List[Card]
    def __init__(self, cardSize, cards) -> None:
        self.cards = list(cards)
        self.cardSize = cardSize


    def getAllImagesAsTuples(self, cardSizeInInches, imageOutputDirPath:Path):
        raise NotImplementedError()
    
    def getCardSize(self):
        return self.cardSize

class PdfSize(object):

    def __init__(self, widthInInches, heightInInches) -> None:
        self.width = widthInInches * POINTS_PER_IN
        self.height = heightInInches * POINTS_PER_IN
        self.width_margin = MARGIN_IN_PTS
        self.height_margin = MARGIN_IN_PTS
        
        self.min_width = self.width_margin
        self.max_width = self.width - self.width_margin

        self.min_height = self.height_margin
        self.max_height = self.height - self.height_margin


    def generateTiledCoordinates(self, tile_width, tile_height):
        width_range = self.max_width - self.min_width
        width_count = int(width_range // tile_width)
        width_surplus = width_range - (width_count * tile_width)
        width_padding = width_surplus / width_count

        height_range = self.max_height - self.min_height
        height_count = int(height_range // tile_height)
        height_surplus = height_range - (height_count * tile_height)
        height_padding = height_surplus / height_count

        new_box_width = tile_width + width_padding
        new_box_height = tile_height + height_padding

        coordinates = list()
        backCoordinates = list()
        for h in range(height_count):
            for w in range(width_count):
                height_pixels = int ((self.min_height + (height_padding/2) + (h * new_box_height)) )
                width_pixels = int( (self.min_width + (width_padding/2) + (w * new_box_width)))
                coordinates.append((width_pixels, height_pixels))
                backCoordinates.append((width_pixels, int(self.max_height-height_pixels-tile_height)))
            

        
        return coordinates, backCoordinates
    

    def makePDFFromCardCollection(self, cardCollection:CardCollection, outputPath:Path, tempPath):

        tuples = cardCollection.getAllImagesAsTuples(cardCollection.getCardSize(), tempPath)
        return self.makePDF(tuples, outputPath, cardCollection.getCardSize())



    def makePDF(self, frontAndBackImages:list[tuple[Path, Path]], outputPath:Path, imageSizeInInches:tuple[float, float]):

        imageWidth = imageSizeInInches[0] * POINTS_PER_IN
        imageHeight = imageSizeInInches[1]*POINTS_PER_IN
        coordinates, backCoordinates = self.generateTiledCoordinates(imageWidth, imageHeight)

        myfile = Canvas(str(outputPath), pagesize=(self.width, self.height))
        count = 0
        while count < len(frontAndBackImages):
            nextPage = list()
            for i, (x,y) in enumerate(coordinates):
                if count >= len(frontAndBackImages):
                    break
                frontImage, backImage = frontAndBackImages[count]
                myfile.drawImage(str(frontImage), x,y, width=imageWidth,height=imageHeight, mask='auto')
                if backImage is not None:
                    nextPage.append((i,backImage))
                count+=1

            # To start the next page you must first render this canvas then call draw again 
            myfile.showPage()
            for i,image in nextPage:
                x,y = backCoordinates[i]
                myfile.drawImage(str(image), x,y, width=imageWidth,height=imageHeight, mask='auto')
            if len(nextPage)> 0:
                myfile.showPage()

        myfile.save()

            



                
            


