""" Mitype main app script """

import curses
import curses.ascii
import math
import os
import random
import sqlite3
import sys
import time


class App:

    """ Class App """

    current_word, current_string, key, text = '', '', '', ''
    tokens = []
    first_key_pressed = False
    start_time = i = mode = end_time = 0

    win_width = 0

    line_count = 0
    curr_wpm = 0
    key_strokes = []

    @staticmethod
    def directory_path():
        """ Get full path of directory where this file is stored """
        path = os.path.abspath(__file__)
        last_index = 0
        slash_character1 = '\\'
        slash_character2 = '/'
        for idx, character in enumerate(path):
            if character in (slash_character1, slash_character2):
                last_index = idx
        return path[0:last_index+1]

    def search(self, entry_id):
        """ Fetch row based on supplied ID """
        path_str = self.directory_path()+"data.db"
        conn = sqlite3.connect(path_str)
        cur = conn.cursor()
        cur.execute("SELECT txt FROM data where id=?", (entry_id,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def generate(self):
        """ Generate a random integer and return text string from database """
        number_of_text_entries = 6000
        string = self.search(random.randrange(1, number_of_text_entries + 1))
        return string[0][0]

    @staticmethod
    def change_index(string1, string2):
        """ Return index at which there is a change in strings """
        if len(string1) == 0:
            return 0
        length = min(len(string1), len(string2))
        for i in range(length):
            if string1[i] != string2[i]:
                return i
        return length

    def get_wpm(self, txt, start_time):
        """ Return speed in WPM """
        time_taken = 60 * len(txt) / self.get_time_elasped(start_time)
        return "{0:.2f}".format(time_taken)

    @staticmethod
    def get_time_elasped(start_time):
        """ Get time elapsed from initial keypress """
        return time.time() - start_time

    @staticmethod
    def count_lines(string, win_width):
        """ Count number of lines required for displaying sample text """
        return int(math.ceil(len(string) / win_width))

    @staticmethod
    def is_escape(key):
        """ Detect ESC key """
        if len(key) == 1:
            return ord(key) == curses.ascii.ESC
        return False

    @staticmethod
    def is_backspace(key):
        """ Detect BACKSPACE key """
        if key in ('KEY_BACKSPACE', '\b'):
            return True
        if len(key) == 1:
            return ord(key) == curses.ascii.BS
        return False

    @staticmethod
    def get_dimensions(win):
        """ Return width of terminal window """
        return int(win.getmaxyx()[1])

    @staticmethod
    def initialize():
        """ Initialize color pairs for curses """
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_CYAN)
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

    def setup_print(self, win):
        """ Print setup text """
        win.addstr(0, 0, ' '*(self.win_width), curses.color_pair(3))
        win.addstr(0, 0, ' Made by Mithil', curses.color_pair(3))
        win.addstr(2, 0, self.text, curses.A_BOLD)

    def key_printer(self, win, key):
        """ Print supplied key to terminal """
        if self.is_escape(key):
            sys.exit(0)

        elif self.is_backspace(key):
            if len(self.current_word) > 0:
                self.current_word = self.current_word[0:len(
                    self.current_word)-1]
                self.current_string = self.current_string[0:len(
                    self.current_string)-1]

        elif key == ' ':
            if self.current_word == self.tokens[self.i]:
                self.i += 1
                self.current_word = ''
            else:
                self.current_word += ' '
            self.current_string += ' '

        elif len(key) == 1:
            self.current_word += key
            self.current_string += key

        win.addstr(self.line_count, 0, ' '*self.win_width)
        win.addstr(self.line_count, 0, self.current_word)

        win.addstr(2, 0, self.text, curses.A_BOLD)
        win.addstr(2, 0, self.text[0:len(self.current_string)], curses.A_DIM)

        index = self.change_index(self.current_string, self.text)
        win.addstr(2+index//self.win_width, index % self.win_width,
                   self.text[index:len(self.current_string)], curses.color_pair(2))

        if index == len(self.text):
            win.addstr(self.line_count, 0, "Your typing speed is ")
            if self.mode == 0:
                self.curr_wpm = self.get_wpm(self.tokens, self.start_time)
            win.addstr(self.curr_wpm,
                       curses.color_pair(1))
            win.addstr(' WPM ')

            win.addstr(self.line_count+2, 0,
                       "Press enter to see a replay!", curses.color_pair(6))

            if self.mode == 0:
                self.mode = 1
                for k in range(len(self.key_strokes)-1, 0, -1):
                    self.key_strokes[k][0] -= self.key_strokes[k-1][0]
            self.key_strokes[0][0] = 0
            self.first_key_pressed = False
            self.end_time = time.time()
            self.current_string = ''
            self.current_word = ''
            self.i = 0
            # for k in range(len(self.key_strokes)):
            #     self.key_strokes[k][0] -= self.start_time

            self.start_time = 0

    def main(self, win):
        """ Main """
        curses.initscr()
        self.initialize()
        win.nodelay(True)
        self.text = self.generate()
        self.tokens = self.text.split()

        self.win_width = self.get_dimensions(win)

        self.line_count = self.count_lines(self.text, self.win_width) + 2 + 1

        self.setup_print(win)

        while True:

            if self.mode == 0:
                try:
                    key = win.getkey()
                except curses.error:
                    continue

                if not self.first_key_pressed:
                    self.start_time = time.time()
                    self.first_key_pressed = True

                self.key_strokes.append([time.time(), key])

                self.key_printer(win, key)

            elif self.mode == 1:
                key = ''
                try:
                    key = win.getkey()
                except curses.error:
                    pass
                if key == '\n':
                    win.addstr(self.line_count+2, 0, ' '*self.win_width)
                    self.setup_print(win)
                    for j in self.key_strokes:
                        time.sleep(j[0])
                        self.key_printer(win, j[1])
                        key_within_replay = ''
                        try:
                            key_within_replay = win.getkey()
                        except curses.error:
                            pass
                        if self.is_escape(key_within_replay):
                            sys.exit(0)
                        win.refresh()

                elif self.is_escape(key):
                    sys.exit(0)

            win.refresh()

    def start(self):
        """ Start app """
        curses.wrapper(self.main)
