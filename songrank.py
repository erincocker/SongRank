import csv
from random import choice, randint
import json
import pygame

pygame.init()

pink_bg = (239, 208, 202)
teal = (15, 163, 177)
pink = (219, 83, 117)
navy = (28, 48, 65)
lilac = (163, 149, 198)
bigger_font = pygame.font.SysFont("Calibri", 80, bold=True)
big_font = pygame.font.SysFont("Calibri", 60, bold=True)
font = pygame.font.SysFont("Calibri", 30, bold=True)


# (each string in text is a new line)
# display (multiple) lines of text centred at (x,y)
def display_text(
    surface, text: list, font: pygame.font.Font, colour: tuple, x: int, y: int
):
    height = font.render(text[0], True, colour).get_height()
    starting_y = y - (height * len(text) / 2)

    for row, line in enumerate(text):
        img = font.render(line, True, colour)
        surface.blit(img, (x - (img.get_width() / 2), starting_y + row * height))


# button class based on coding with russ' tutorial
class Button:
    def __init__(
        self,
        centre_x: int,
        centre_y: int,
        image1,
        image2,
        desired_width: int,
        desired_height: int,
    ):
        self.image1 = pygame.transform.scale(image1, (desired_width, desired_height))
        self.image2 = pygame.transform.scale(image2, (desired_width, desired_height))
        self.rect = self.image1.get_rect()
        self.rect.center = (centre_x, centre_y)
        self.clicked = False

    # draw button on screen and check for button press
    # if button press, return True
    def draw(self, surface):
        button_press = False  # true when button gets pressed
        position = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0] == 1:
            if self.rect.collidepoint(position) and self.clicked == False:
                button_press = True  # only true if the button goes from not pressed
                # to pressed while on the button
            self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # show a different coloured border if mouse is hovering over the button.
        if self.rect.collidepoint(position):
            surface.blit(self.image2, (self.rect.x, self.rect.y))
        else:
            surface.blit(self.image1, (self.rect.x, self.rect.y))

        return button_press


# inner mechanisms
class SongLists:
    def __init__(self):
        # initial list: songs yet to be added to master list
        # though it's a dictionary so we can access songs by id
        self.initial_list = {}
        for i in range(len(Functions.Songs)):
            self.initial_list[i] = ["" for j in range(len(Functions.Songs))]
            # initial_list[i][j] will be '+' if song i is better than song j
            # '-' if song i is worse than song j
            # or '' if they haven't been compared

        # master list: ranked songs. gradually add to this until completion
        self.master_list = []

    # save info from a comparison to the initial list
    def make_comparison(self, song_I: int, song_M: int, better: int):
        if better == 1:
            self.initial_list[song_I][song_M] = "+"
        elif better == 2:
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
        if upperbound == lowerbound:
            self.master_list.insert(upperbound, songid)
            self.initial_list.pop(songid)
            return

        # otherwise, add any extra inferred info to initial list and move on
        for i in range(0, upperbound):
            self.initial_list[songid][self.master_list[i]] = "-"
        for i in range(lowerbound + 1, len(self.master_list)):
            self.initial_list[songid][self.master_list[i]] = "+"

    # place one random song into the masterlist to begin with
    def first_song(self):
        songid = randint(0, len(Functions.Songs))
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


# contains mostly the functions that are directly accessed by the app class
class Functions:
    Songs = []  # full list of songs and albums, not to be changed

    def __init__(self):
        self.get_all_songs("songs multiline form.txt")
        self.songlists = SongLists()

    # save the list of all songs to Functions.Songs
    def get_all_songs(self, filename: str):
        with open(filename) as file:
            for line in csv.reader(file, delimiter=",", escapechar="\\"):
                song_name = [part for part in line[0:-1]]
                Functions.Songs.append([song_name, line[-1]])

    # want to choose one song from initial list then one from masterlist that
    # hasn't yet been compared to the first song
    # returns id of the songs to be compared, song S from initial list, song M from Masterlist
    def choose_pair(self):
        song_I = choice(list(self.songlists.initial_list.keys()))
        # second song must also be within the upper and lower bounds of song_I
        # otherwise the comparison is redundant
        upperbound, lowerbound = self.songlists.find_bounds(song_I)

        if lowerbound - upperbound <= 10:
            song_M = choice(self.songlists.master_list[upperbound:lowerbound])
        else:
            # if bounds are far apart, choose a song near the midpoint of the bounds
            # (this is more efficient)
            # but not exactly in the middle - this would mean boring repetition of songs
            optimal_song_position = (upperbound + lowerbound) // 2
            randomised_song_position = randint(
                optimal_song_position - 5, optimal_song_position + 5
            )
            song_M = self.songlists.master_list[randomised_song_position]
        return song_I, song_M

    # load previous ranking data
    def load_data(self):
        self.songlists.importdata("songsranked.json")
        self.songlists.initial_list = {
            int(k): self.songlists.initial_list[k] for k in self.songlists.initial_list
        }  # json files turn dictionary keys that are integers into strings
        # must turn them back into integers

    # start a new ranking
    def new_ranking(self):
        self.songlists.first_song()

    # return a pair of songs (both name and album)
    def get_new_song_names(self):
        self.song_I, self.song_M = self.choose_pair()
        return Functions.Songs[self.song_I], Functions.Songs[self.song_M]

    # add info about which song is better to the song lists
    def song_clicked(self, which_song: int):
        self.songlists.make_comparison(self.song_I, self.song_M, which_song)
        self.songlists.check(self.song_I)

    # save songlists
    def save_data(self):
        self.songlists.savedata("songsranked.json")

    # prints current master list in terminal
    def print_masterlist(self):
        print()
        for songid in self.songlists.master_list:
            print(" ".join(Functions.Songs[songid][0]))


# takes care of user interface
class App:
    def __init__(self):
        pygame.display.set_caption("Song Ranker")
        self.window = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        self.load_images()

        self.starting_screen()

    # load in album graphics and button graphics
    def load_images(self):
        self.images1 = {}
        self.images2 = {}
        for name in [
            "button",
            "Debut",
            "Fearless",
            "SN",
            "Red",
            "1989",
            "Rep",
            "Lover",
            "Folklore",
            "Evermore",
            "Midnights",
        ]:
            self.images1[name] = pygame.image.load("images/" + name + ".png")
            self.images2[name] = pygame.image.load("images2/" + name + ".png")

    # welcome screen containing 'continue' and 'new' buttons
    def starting_screen(self):
        self.functions = Functions()
        load_button = Button(
            170, 230, self.images1["button"], self.images2["button"], 250, 75
        )
        new_ranking_button = Button(
            470, 230, self.images1["button"], self.images2["button"], 250, 75
        )
        start_main_loop = False

        while True:
            self.window.fill(pink_bg)

            if load_button.draw(self.window):
                self.functions.load_data()
                start_main_loop = True
            if new_ranking_button.draw(self.window):
                self.functions.new_ranking()
                start_main_loop = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                # only start main loop once mouse button is up
                # to prevent accidental extra clicking when screen changes
                if event.type == pygame.MOUSEBUTTONUP and start_main_loop:
                    self.main_loop()

            display_text(self.window, ["Continue"], big_font, navy, 170, 230)
            display_text(self.window, ["New"], big_font, navy, 470, 230)
            pygame.display.flip()
            self.clock.tick(60)

    def main_loop(self):
        song1, song2, song1_button, song2_button = self.new_song_buttons()
        (
            save_button,
            quit_button,
            display_list_button,
        ) = self.initialise_main_loop_buttons()
        song_clicked = False

        while True:
            display_data_saved = False
            self.window.fill(pink_bg)
            # pygame.draw.rect(self.window, navy, (75, 125, 210, 210))
            # pygame.draw.rect(self.window, navy, (355, 125, 210, 210))

            if song1_button.draw(self.window):
                self.functions.song_clicked(1)
                song_clicked = True
            if song2_button.draw(self.window):
                self.functions.song_clicked(2)
                song_clicked = True
            if save_button.draw(self.window):
                self.functions.save_data()
                display_data_saved = True
            if quit_button.draw(self.window):
                self.starting_screen()
            if display_list_button.draw(self.window):
                self.functions.print_masterlist()

            self.display_main_loop_text(song1[0], song2[0])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONUP and song_clicked:
                    song1, song2, song1_button, song2_button = self.new_song_buttons()
                    song_clicked = False

            if display_data_saved:
                display_text(
                    self.window,
                    ["Data Saved"],
                    bigger_font,
                    pink,
                    320,
                    80,
                )
                pygame.display.flip()
                self.clock.tick(1 / 2)

            pygame.display.flip()
            self.clock.tick(60)

    # get the next two songs ready to show in the application
    def new_song_buttons(self):
        song1, song2 = self.functions.get_new_song_names()
        song1_button = Button(
            180, 230, self.images1[song1[1]], self.images2[song1[1]], 200, 200
        )
        song2_button = Button(
            460, 230, self.images1[song2[1]], self.images2[song2[1]], 200, 200
        )
        return song1, song2, song1_button, song2_button

    def initialise_main_loop_buttons(self):
        save_button = Button(
            490, 30, self.images1["button"], self.images2["button"], 80, 40
        )
        quit_button = Button(
            590, 30, self.images1["button"], self.images2["button"], 80, 40
        )
        display_list_button = Button(
            90, 30, self.images1["button"], self.images2["button"], 160, 40
        )
        return save_button, quit_button, display_list_button

    def display_main_loop_text(self, song1, song2):
        display_text(
            self.window,
            song1,
            font,
            navy,
            180,
            230,
        )

        display_text(
            self.window,
            song2,
            font,
            navy,
            460,
            230,
        )

        display_text(
            self.window,
            ["Save"],
            font,
            navy,
            490,
            30,
        )

        display_text(
            self.window,
            ["Quit"],
            font,
            navy,
            590,
            30,
        )

        display_text(
            self.window,
            ["Display List"],
            font,
            navy,
            90,
            30,
        )

        display_text(
            self.window,
            ["OR"],
            font,
            navy,
            320,
            230,
        )


application = App()
