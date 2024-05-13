import unittest
from main import *

class TestAssetGetter(unittest.TestCase):
    
    assetGetter = AssetGetter(Path("assets"))

    def test_getLevelIcon(self):
        imagePath = self.assetGetter.getLevelIcon()
        assert imagePath.is_file()

        
    def test_getResourceCardBackPath(self):
        imagePath = self.assetGetter.getResourceCardBackPath()
        assert imagePath.is_file()
        
    
    def test_getVipCardBackImageRaw(self):
        imagePath = self.assetGetter.getVipCardBackImageRaw()
        assert imagePath.is_file()

    # def test_getAvatarImagesPath(self):
    #     imagePaths = self.assetGetter.getAvatarImagesPath()

    #     assert len(imagePaths) >= 5

    #     for imagePath in imagePaths: 
    #         assert imagePath.is_file()
        
    
    def test_getVipImagePaths(self):
        imagePaths = self.assetGetter.getVipImagePaths()

        assert len(imagePaths) >= 10

        for imagePath in imagePaths: 
            assert imagePath.is_file()
    
    def test_getResourceImagePath(self):
        for type in ResourceType:
            if (type == ResourceType.Avatar):
                continue
            imagePath = self.assetGetter.getResourceImagePath(type)
            assert imagePath.is_file()
        
    def test_getResourceCardImagePaths(self):
        for type in ResourceType:
            if (type == ResourceType.Avatar):
                continue
            imagePaths = self.assetGetter.getResourceCardImagePaths(type)
            assert len(imagePaths) >= 30
            for imagePath in imagePaths:
                assert imagePath.is_file()
        


if __name__ == '__main__':
    unittest.main()