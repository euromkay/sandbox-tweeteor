from threading import Thread
from Tkinter import *
from ttk import *
import sys, pygame, logging

# Allows the user to interact with the program (view/change search parameters, exit). Currently only controllable through the terminal.
class Controller(Thread):
    def __init__(self, searcher):
        Thread.__init__(self, name = 'Controller')
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
        self.quitButton = Button(self)
        self.quitButton['text'] = "Quit"
        self.quitButton['command'] = self.quit
        self.quitButton.grid(row = 0)
        self.hashtagList = ListFrame("Hashtags", searcher.addHashtag, searcher.removeHashtag, master = self)
        self.hashtagList.grid(row = 1, column = 0, padx = 5)
        self.userList = ListFrame("Users", searcher.addUser, searcher.removeUser, master = self)
        self.userList.grid(row = 1, column = 1, padx = 5)
        self.excludedWordList = ListFrame("Excluded Words", searcher.excludeWord, searcher.removeExcludedWord, master = self)
        self.excludedWordList.grid(row = 1, column = 2, padx = 5)
        self.excludedUserList = ListFrame("Excluded Users", searcher.excludeUser, searcher.removeExcludedUser, master = self)
        self.excludedUserList.grid(row = 1, column = 3, padx = 5)

class ListFrame(LabelFrame):
    def __init__(self, name, addHandler, removeHandler, master = None):
        LabelFrame.__init__(self, master)
        self['text'] = name
        self.addHandler = addHandler
        self.removeHandler = removeHandler
        self.list = Listbox(self)
        self.list.grid(row = 0, columnspan = 2)
        self.list.bind("<Button-1>", lambda event: self.contextMenu.unpost())
        self.list.bind("<Button-3>", self.openMenu)
        self.contextMenu = Menu(self, tearoff = 0)
        self.contextMenu.add_command(label = "Remove", command = self.remove)
        self.input = Entry(self)
        self.input.bind("<Return>", self.add)
        self.input.grid(row = 1, columnspan = 2)
        self.addButton = Button(self)
        self.addButton['text'] = "Add"
        self.addButton['command'] = self.add
        self.addButton.grid(row = 2, column = 0, sticky = W+E)
        self.removeButton = Button(self)
        self.removeButton['text'] = "Remove"
        self.removeButton['command'] = self.remove
        self.removeButton.grid(row = 2, column = 1, sticky = W+E)
    def add(self, event = None):
        self.list.insert(END, self.input.get())
        self.addHandler(self.input.get())
        self.input.delete(0, END)
    def remove(self):
        deleted = self.list.get(ACTIVE)
        self.list.delete(ACTIVE)
        self.removeHandler(deleted)
    def openMenu(self, event):
        index = self.list.index("@" + str(event.x) + "," + str(event.y))
        if index < 0:
            return
        self.contextMenu.post(event.x_root, event.y_root)
        self.list.activate(index)
        self.list.selection_clear(0, END)
        self.list.selection_set(ACTIVE)
