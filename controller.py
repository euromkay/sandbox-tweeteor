import sys
from threading import Thread
from Tkinter import Tk, Listbox, Menu, END, ACTIVE, W, E
from ttk import Frame, LabelFrame, Button, Entry

import pygame


class Controller(Thread):

    def __init__(self, searcher):
        Thread.__init__(self, name='Controller')
        self.searcher = searcher

    def run(self):
        root = Tk()
        app = GUI(self.searcher, master=root)
        app.mainloop()
        self.searcher.exit.set()
        self.searcher.join()
        pygame.quit()
        sys.exit()


class GUI(Frame):

    def __init__(self, searcher, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.exit = Button(self)
        self.exit['text'] = "Quit"
        self.exit['command'] = self.quit
        self.exit.grid(row=0)
        self.hashtags = ListFrame(
            "Hashtags",
            searcher.add_hashtag,
            searcher.remove_hashtag,
            master=self)
        self.hashtags.grid(row=1, column=0, padx=5)
        self.users = ListFrame(
            "Users",
            searcher.add_user,
            searcher.remove_user,
            master=self)
        self.users.grid(row=1, column=1, padx=5)
        self.excluded_words = ListFrame(
            "Excluded Words",
            searcher.exclude_word,
            searcher.remove_excluded_word,
            master=self)
        self.excluded_words.grid(row=1, column=2, padx=5)
        self.excluded_words = ListFrame(
            "Excluded Users",
            searcher.exclude_user,
            searcher.remove_excluded_user,
            master=self)
        self.excluded_words.grid(row=1, column=3, padx=5)


class ListFrame(LabelFrame):

    def __init__(self, name, add_handler, remove_handler, master=None):
        LabelFrame.__init__(self, master)
        self['text'] = name
        self.add_handler = add_handler
        self.remove_handler = remove_handler
        self.list = Listbox(self)
        self.list.grid(row=0, columnspan=2)
        self.list.bind("<Button-1>", lambda event: self.context_menu.unpost())
        self.list.bind("<Button-3>", self.open_menu)
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Remove", command=self.remove)
        self.input = Entry(self)
        self.input.bind("<Return>", self.add)
        self.input.grid(row=1, columnspan=2)
        self.add_button = Button(self)
        self.add_button['text'] = "Add"
        self.add_button['command'] = self.add
        self.add_button.grid(row=2, column=0, sticky=W+E)
        self.remove_button = Button(self)
        self.remove_button['text'] = "Remove"
        self.remove_button['command'] = self.remove
        self.remove_button.grid(row=2, column=1, sticky=W+E)

    def add(self, event):
        self.list.insert(END, self.input.get())
        self.add_handler(self.input.get())
        self.input.delete(0, END)

    def remove(self):
        deleted = self.list.get(ACTIVE)
        self.list.delete(ACTIVE)
        self.remove_handler(deleted)

    def open_menu(self, event):
        index = self.list.index("@" + str(event.x) + "," + str(event.y))
        if index < 0:
            return
        self.context_menu.post(event.x_root, event.y_root)
        self.list.activate(index)
        self.list.selection_clear(0, END)
        self.list.selection_set(ACTIVE)
