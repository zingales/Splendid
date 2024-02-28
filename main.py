import csv

from splendid import ResourceType, ResourceCard

conversionColorToResourceType = {
    'Black': ResourceType.Air,
    'White': ResourceType.WhiteLotus,
    'Blue': ResourceType.Water,
    'Green':ResourceType.Earth,
    'Red':ResourceType.Fire,
    'Gold':ResourceType.Avatar
}

def loadResourceCardsFromCsv(csvFile):
    with open(csvFile, newline='\n') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar="'")
        cards = list()
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
                    requirements[resourceType] = 0 if row[ogColor] == '' else int(row[ogColor])
                cards.append(ResourceCard(produces=generates, requires=requirements,level=cardLevel,victoryPoints=victoryPoints))
            except (KeyError,ValueError) as e:
                raise ValueError(f"invalid row at {rowCount}\RowContents: {row}")

            rowCount+=1

        return cards


def main():
    resourceCardsCSV = "assets/resourceCards.csv"
    print(f"{resourceCardsCSV}")
    cards = loadResourceCardsFromCsv(resourceCardsCSV)
    print(f"number of cards {len(cards)}")
    print(f"card 0 {cards[0]}")


if __name__ == "__main__":
    main()