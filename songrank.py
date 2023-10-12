import csv
from random import choice, randint
import json


class SongLists:
    def __init__(self):
        # initial list: songs yet to be added to master list
        # though it's a dictionary so we can access songs by id
        self.initial_list = {}
        for i in range(len(App.Songs)):
            self.initial_list[i] = []
            for j in range(len(App.Songs)):
                self.initial_list[i].append("")
            # initial_list[i][j] will be '+' if song i is better than song j
            # '-' if song i is worse than song j
            # or '' if they haven't been compared

        # master list: ranked songs. gradually add to this until completion
        self.master_list = []

    # save info from a comparison to the initial list
    def make_comparison(self, song_I: int, song_M: int, better: str):
        if better == "1":
            self.initial_list[song_I][song_M] = "+"
        elif better == "2":
            self.initial_list[song_I][song_M] = "-"

    # return the bounds for the song's possible position in the masterlist
    # note upperbound should be < lowerbound as a smaller number means better position
    # it is an error with my programming if upperbound > lowerbound
    def find_bounds(self, songid: int):
        upperbound = 0
        lowerbound = len(self.master_list)
        for i in range(len(self.master_list)):
            comparison = self.initial_list[songid][self.master_list[i]]
            if comparison == "-":
                # i.e. if the song is worse than the song in the ith position in masterlist
                upperbound = max(upperbound, i + 1)
            elif comparison == "+":
                lowerbound = min(lowerbound, i)

        return upperbound, lowerbound

    # check if song1 can be added to masterlist
    # if not, add any extra info to song1
    # i.e. if songA better than songB also implies songA better than songC,
    # then add this info to songA
    def check(self, songid: int):
        upperbound, lowerbound = self.find_bounds(songid)

        if upperbound > lowerbound:
            raise ValueError("CONTRADICTION!")

        # if upper = lower, position in masterlist is determined
        # place the song in masterlist and remove it from initial list
        elif upperbound == lowerbound:
            self.master_list.insert(upperbound, songid)
            self.initial_list.pop(songid)

        # otherwise, add any extra inferred info to initial list and move on
        else:
            for i in range(0, upperbound):
                self.initial_list[songid][self.master_list[i]] = "-"
            for i in range(lowerbound + 1, len(self.master_list)):
                self.initial_list[songid][self.master_list[i]] = "+"

    # place one random song into the masterlist to begin with
    def first_song(self):
        songid = randint(0, len(App.Songs))
        self.initial_list.pop(songid)
        self.master_list.insert(0, songid)

    # saved data is a json file
    # the file contains a list containing the initial list and master list
    def savedata(self, filename: str):
        with open(filename, "w") as file:
            file.write(json.dumps([self.initial_list, self.master_list]))

    def importdata(self, filename: str):
        with open(filename) as file:
            [self.initial_list, self.master_list] = json.loads(file.read())


class App:
    Songs = []  # full list of songs and albums, not to be changed

    def __init__(self):
        pass

    def get_songs(self, filename: str):
        with open(filename) as file:
            for line in csv.reader(file, delimiter=","):
                if len(line) == 1:
                    App.Songs.append([line[0]])
                elif len(line) == 2:
                    App.Songs.append([line[0], line[1]])

    # want to choose one song from initial list then one from masterlist that
    # hasn't yet been compared to the first song
    # returns id of the songs to be compared, song S from initial list, song M from Masterlist
    def choose_pair(self, songlists: SongLists):
        song_I = choice(list(songlists.initial_list.keys()))
        # second song must also be within the upper and lower bounds of song_I
        # otherwise the comparison is redundant
        upperbound, lowerbound = songlists.find_bounds(song_I)
        song_M = choice(songlists.master_list[upperbound:lowerbound])
        return song_I, song_M

    def load_data(self, songlists: SongLists):
        songlists.importdata("songsranked.json")
        songlists.initial_list = {
            int(k): songlists.initial_list[k] for k in songlists.initial_list
        }  # json files turn dictionary keys that are integers into strings
        # must turn them back into integers
        print()
        return songlists

    def execute(self):
        print(
            """
        Welcome to Song Ranker
              
        At each pair of songs, enter 1 to choose the first song,
        or 2 to choose the second
              
        At any point, type in...
        MasterList: to see the ranked list so far.
        Save: to save and quit

              
        """
        )

        # filename = input("First enter the file name: ")
        self.get_songs("songs.txt")

        songlists = SongLists()

        if input("Load saved data? (y/n): ") == "y":
            songlists = self.load_data(songlists)

        if songlists.master_list == []:
            songlists.first_song()

        # will later add in a command list, option to exit, option to save list so far, etc.
        while True:
            # first get a pair of songs
            song_I, song_M = self.choose_pair(songlists)
            # user chooses their favourite and the initial list is updated
            print("Which is better?")
            print(f"Song 1: {App.Songs[song_I][0]}")
            print(f"Or Song 2: {App.Songs[song_M][0]}")
            better = input("1 or 2: ")

            if better == "1" or better == "2":
                songlists.make_comparison(song_I, song_M, better)
            elif better == "MasterList":
                self.print_masterlist(songlists)
            elif better == "Save":
                songlists.savedata("songsranked.json")
                quit()
            print()

            songlists.check(song_I)
            print()

            if len(songlists.master_list) == len(App.Songs):
                break

        self.print_masterlist(songlists)

    def print_masterlist(self, songlists: SongLists):
        print()
        for songid in songlists.master_list:
            print(App.Songs[songid][0])


application = App()
application.execute()
