import csv
import traceback

from splendid import ResourceType, ResourceCard

conversionColorToResourceType = {
    'Black': ResourceType.Air,
    'White': ResourceType.WhiteLotus,
    'Blue': ResourceType.Water,
    'Green':ResourceType.Earth,
    'Red':ResourceType.Fire,
    'Gold':ResourceType.Avatar
}


class BadResourceCSVRow(ValueError):
    def __init__(self, csvRowNumber, rowContents, error):            
        # Call the base class constructor with the parameters it needs
        super().__init__(f"Bad CSV Row. Row no.{csvRowNumber}, {error}: row contents {rowContents}")
            
        # Now for your custom code...
        self.rowNumber = csvRowNumber
        self.previousError = error
        self.rowContents = rowContents


def loadResourceCardsFromCsv(csvFile):
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
                    requirements[resourceType] = 0 if row[ogColor] == '' else int(row[ogColor])
                cards.append(ResourceCard(produces=generates, requires=requirements,level=cardLevel,victoryPoints=victoryPoints))
            except (KeyError,ValueError) as e:
                customError = BadResourceCSVRow(rowCount, f"{row}", e)
                errors.append(customError)

            rowCount+=1

        return cards, errors


def main():
    resourceCardsCSV = "assets/resourceCards.csv"
    print(f"{resourceCardsCSV}")
    cards,errors = loadResourceCardsFromCsv(resourceCardsCSV)
    print(f"number of cards {len(cards)}")
    print(f"card 0 {cards[0]}")
    print(f"number of bad rows {len(errors)}")
    if len(errors) > 0:
        print(f"{errors[0]}")


if __name__ == "__main__":
    main()