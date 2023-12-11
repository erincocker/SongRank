# Program for when new songs need to be added to the list.
# Updates my saved data so the initial list is now the right format
# without changing any of the necessary comparison data.

# Must also change the file 'songs multiline form.txt'
# manually whenever this program is used.

# Careful! This program overwrites the original file that you give
import json


def addsongs(originalFile: str, originalNumOfSongs: int, numOfAddedSongs: int):
    with open(originalFile) as file:
        initialList, masterList = json.loads(file.read())
    # change keys to integers as json turns them into strings
    initialList = {int(k): initialList[k] for k in initialList}

    # first add items in the dictionary for the new songs
    for j in range(numOfAddedSongs):
        initialList[originalNumOfSongs + j] = ["" for i in range(originalNumOfSongs)]

    # now adjust each item so they are long enough to contain info about the new songs
    for key in initialList:
        initialList[key] += ["" for j in range(numOfAddedSongs)]

    # save new file
    with open(originalFile, "w") as file:
        file.write(json.dumps([initialList, masterList]))


def main():
    addsongs("songsranked.json", 201, 0)


main()
