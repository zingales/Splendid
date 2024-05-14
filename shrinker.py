from PIL import Image
from pathlib import Path

def symmetricalCrop(img, shrinkX, shrinkY):
    img_size_x, img_size_y = img.size
    return img.crop(box=(shrinkX,shrinkY,img_size_x-shrinkX,img_size_y-shrinkY))


def lama(total_length, number_of_divisions, offset, division_size):
    
    interstitialSpaces = ((total_length - 2*offset) - (number_of_divisions*division_size)) // number_of_divisions
    startingXOffset = offset + interstitialSpaces//2

    to_return = list()
    for index in range(0, number_of_divisions):
        to_return.append(startingXOffset+ (index * (interstitialSpaces+division_size)))

    return to_return

if __name__ == "__main__":

    OUTPUT_DPI = 150
    
    inputFolder = Path("/Users/gzingales/Downloads/FireShot")
    outputFolder = Path("/Users/gzingales/Downloads/Trimmed")
    shrinkX = 396
    shrinkY = 0

    count = 0

    for inputPath in inputFolder.glob("*.png"):
        img = Image.open(inputPath)
        smaller_image = symmetricalCrop(img, shrinkX, shrinkY)
        
        outputPath = outputFolder/f"Fireshot_{count}.png"
        smaller_image.save(outputPath, dpi=(OUTPUT_DPI,OUTPUT_DPI))
        count+=1
    