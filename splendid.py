from pathlib import Path
from enum import Enum


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

class ResourceToken(object):
    resourceType:ResourceType
    imagePath: Path
    renderedFrontImage:Path 

    def __init__(self, resourceType:ResourceType, imagePath=None) -> None:
        self.resourceType = resourceType
        self.imagePath = imagePath
        self.renderedFrontImage = None

class VIPCard(object):
    requires:dict[ResourceType,int]
    victoryPoints:int
    imagePath: Path

    def __init__(self, requires:dict[ResourceType,int], victoryPoints:int) -> None:
        self.requires = requires
        self.victoryPoints = victoryPoints
        self.imagePath = None

    def __repr__(self) -> str:
        resrouceStrings = list() 
        for resource, count in self.requires.items():
            if count == 0:
                continue
            resrouceStrings.append(f"{resource}: {count}")
        return f"Splendid.VIPCard(VP: {self.victoryPoints}, requires:[{', '.join(resrouceStrings)}], imagePath: {self.imagePath}"
    

class ResourceCard(object):
    produces:ResourceType
    requires:dict[ResourceType,int]
    victoryPoints:int
    level:int
    imagePath: Path
    renderedBackImage: Path
    renderedFrontImage: Path

    def __init__(self, produces:ResourceType, requires:dict[ResourceType,int], level:int, victoryPoints:int) -> None:
        self.produces = produces
        self.requires = requires
        self.victoryPoints = victoryPoints
        self.level = level
        self.imagePath = None
        self.renderedFrontImage = None
        self.renderedBackImage = None


    def __repr__(self) -> str:
        resrouceStrings = list() 
        for resource, count in self.requires.items():
            if count == 0:
                continue
            resrouceStrings.append(f"{resource}: {count}")
        return f"Splendid.ResourceCard(level: {self.level}, produces: {self.produces}, VP: {self.victoryPoints}, requires:[{', '.join(resrouceStrings)}], imagePath: {self.imagePath}"
        
