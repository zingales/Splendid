import unittest
from pathlib import Path
from PIL import Image, ImageDraw

import imageDrawing


class TestImageDrawing(unittest.TestCase):
    
    
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.test_path_image1 = Path("test_assets") / "image1.png"
        self.test_path_icon1 = Path("test_assets") / "icon1.png"

    def test_GuaranteeFolder(self):
        outputPath = Path("output")
        imageDrawing.guaranteeFolder(outputPath)
        assert outputPath.is_dir()
        imageDrawing.guaranteeFolder(outputPath/ "test_output")
        

    def test_GetFont(self):
        imageDrawing.getFont(fontname='Herculanum.ttf', fontsize=50)

    def test_AddNumber(self):
        img = Image.open(self.test_path_image1)
        draw = ImageDraw.Draw(img)
        bg_w, bg_h = img.size
        number = 2
        font = imageDrawing.getFont()
        centeredAt = (bg_h//2, bg_w//2)
        imageDrawing.addNumber(draw, number, centeredAt, font)


    def test_AddCardLevel(self):
        img = Image.open(self.test_path_image1)
        bg_w, bg_h = img.size
        number = 2
        centeredAt = (bg_h//2, bg_w//2)
        icon = Image.open(self.test_path_icon1)
        imageDrawing.addCardLevel(img, number, centeredAt, icon, alignmentHorizontal=True)
        imageDrawing.addCardLevel(img, number, centeredAt, icon, alignmentHorizontal=False)

    def test_Add_border(self):
        img = Image.open(self.test_path_image1)
        border_color = "Black"
        border_size = 10
        
        img = imageDrawing.add_border(img, border_color, border_size, cropInsteadOfShrink=True)
        imageDrawing.add_border(img, border_color, border_size, cropInsteadOfShrink=False)


    def test_Shrink_image(self):
        img = Image.open(self.test_path_image1)
        bg_w, bg_h = img.size
        new_size_pixels = (bg_h//2, bg_w//2)
        fillColor = "Yellow"
        imageDrawing.shrink_image(img, new_size_pixels, fillColor)



if __name__ == '__main__':
    unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestImageDrawing))
    