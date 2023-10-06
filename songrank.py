import csv
from random import choice, sample

#to do next:

#include importing/exporting/saving functionality so user can stop
# and later come back to the same list

#change song picker so it picks optimally: pick the song halfway between
# the upper and lower bounds

#make everything neater and clearer - both on the ui side
# and on the code side


class Song:
    def __init__(self, id: int):
        self.id = id

        #song.compare[i] will be '+' if the song is better than song i
        # '-' if song is worse than song i
        # or '' if they haven't been compared
        self.compare = []
        for i in range(len(App.Songs)):
            self.compare.append('')



#songbook contains songs yet to be added to the master list
#dictionary in the form dictionary[songid] = Song object corresponding to id
#songs to be removed from songbook when they are added to the master list
class SongBook:
    def __init__(self):
        self.songs = {}
        for i in range(len(App.Songs)):
            self.songs[i] = Song(i)
    

    #user says which song is better
    #info is saved to the song objects
    #program checks if either song can go into the master list yet
    def make_comparison(self, song_S: int, song_M: int, better: str):
        if better == '1':
            self.songs[song_S].compare[song_M] = '+'
        elif better == '2':
            self.songs[song_S].compare[song_M] = '-'





class MasterList:
    def __init__(self):
        self.songs = []

    #returns the bounds for the song's possible position in the masterlist
    #note upperbound should be < lowerbound as a smaller number means better position
    #it is an error with my programming if upperbound > lowerbound
    def find_bounds(self, songid: int, songbook: SongBook):
        upperbound = 0 
        lowerbound = len(self.songs)
        for i in range(len(self.songs)):
            comparison = songbook.songs[songid].compare[self.songs[i]]
            if comparison == '-':
                #i.e. if the song is worse than the song in the ith position in masterlist
                upperbound = max(upperbound, i+1)
            elif comparison == '+':
                lowerbound = min(lowerbound, i)
        
        return upperbound, lowerbound

    #check if song1 can be added to masterlist
    #if not, add any extra info to song1 
    # i.e. if songA better than songB also implies songA better than songC,
    # then add this info to songA
    def check(self, songid: int, songbook: SongBook):
        upperbound, lowerbound = self.find_bounds(songid, songbook)

        if upperbound > lowerbound:
            raise ValueError('CONTRADICTION!')
        
        #if upper = lower, position in masterlist is determined
        #place the song in masterlist and remove it from songbook
        elif upperbound == lowerbound:
            self.songs.insert(upperbound, songid)
            songbook.songs.pop(songid)

        #otherwise, add any extra inferred info to songbook and move on
        else:
            for i in range(0, upperbound):
                songbook.songs[songid].compare[self.songs[i]] = '-'
            for i in range(lowerbound+1, len(self.songs)):
                songbook.songs[songid].compare[self.songs[i]] = '+'





class App:
    Songs = [] #full list of songs and albums, not to be changed
    
    def __init__(self):
        pass

    def get_songs(self, filename: str):
        with open(filename) as file:
            for line in csv.reader(file, delimiter=','):
                App.Songs.append([line[0],line[1]])


    #want to choose one song from songbook then one from masterlist that
    # hasn't yet been compared to the first song
    def choose_pair(self, songbook: SongBook, masterlist: MasterList):
        song_S = choice(list(songbook.songs.keys()))
        #second song must also be within the upper and lower bounds of song_S
        #otherwise the comparison is redundant
        upperbound, lowerbound = masterlist.find_bounds(song_S, songbook)
        song_M = choice(masterlist.songs[upperbound:lowerbound])
        return song_S, song_M
    #returns id of the songs to be compared, song S from Songbook, song M from Masterlist


    #for the first comparison as the first comparison must be between two songs from
    # the songbook, as the masterlist starts as empty
    def first_comparison(self, songbook: SongBook, masterlist: MasterList):
        
        song1, song2 = sample(list(songbook.songs.keys()), 2)
        print('Which is better?')
        print(f'Song 1: {App.Songs[song1][0]}')
        print(f'Or Song 2: {App.Songs[song2][0]}')
        better = input('1 or 2: ')
        
        if better == '1':
            masterlist.songs.append(song1)
            masterlist.songs.append(song2)
        elif better == '2':  
            masterlist.songs.append(song2)
            masterlist.songs.append(song1)  
        else:
            print('...1 or 2 plz')
            exit()#to be editsd

        songbook.songs.pop(song1)
        songbook.songs.pop(song2)
        return songbook, masterlist



    def execute(self):
        

        print('''
        Welcome to Song Ranker
              
        At each pair of songs, enter 1 to choose the first song,
        or 2 to choose the second
              
        At any point after the first comparison, enter SongBook to see the songbook
        or enter MasterList to see the list so far.
              
        ''')
        
        filename = input('First enter the file name: ')
        self.get_songs(filename)
        songbook = SongBook()
        masterlist = MasterList()

        if masterlist.songs == []:
            songbook, masterlist = self.first_comparison(songbook, masterlist)
            print()
        #will later add in a command list, option to exit, option to save list so far, etc. 
        while True:
           
            #first get a pair of songs
            song_S, song_M = self.choose_pair(songbook, masterlist)
            #user chooses their favourite and the songbook is updated
            # with the preference
            print('Which is better?')
            print(f'Song 1: {App.Songs[song_S][0]}')
            print(f'Or Song 2: {App.Songs[song_M][0]}')
            better = input('1 or 2: ')
            if better == '1' or better == '2':
                songbook.make_comparison(song_S, song_M, better)
            elif better == 'SongBook':
                print()
                for i in songbook.songs:
                    print(songbook.songs[i])
            elif better == 'MasterList':
                print()
                for songid in masterlist.songs:
                    print(App.Songs[songid][0])
            print()
                
            #check to see if song_S can be placed in the masterlist
            #if so, place it. (other checks also take place)
            masterlist.check(song_S, songbook)
            print()

            if len(masterlist.songs) == len(App.Songs):
                break

        for songid in masterlist.songs:
            print(App.Songs[songid])
        

        

application = App()
application.execute()