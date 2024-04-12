from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import pagesizes
from pathlib import Path


POINTS_PER_IN = 72
MARGIN_IN_PTS = 24

US_LETTER_IN = (
    pagesizes.LETTER[0]/POINTS_PER_IN, 
    pagesizes.LETTER[1]/POINTS_PER_IN
    )

class PdfMaker(object):

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
                height_pixels = int ((self.min_height + (height_padding/2) + (h * new_box_height)))
                width_pixels = int( (self.min_width + (width_padding/2) + (w * new_box_width)) )
                coordinates.append((width_pixels, height_pixels))
                backCoordinates.append((width_pixels, int(self.height-height_pixels-tile_height)))
            

        
        return coordinates, backCoordinates
    


    def makePDF(self, frontAndBackImages:list[tuple[Path, Path]], outputPath:Path, imageSizeInInches:tuple[float, float]):

        imageWidth = imageSizeInInches[0] * POINTS_PER_IN
        imageHeight = imageSizeInInches[1] * POINTS_PER_IN
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
            myfile.showPage()

        myfile.save()

            



                
            


