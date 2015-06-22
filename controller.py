"""A GUI for controlling the search terms used by Tweeteor."""
import logging
from threading import Thread
from Tkinter import Tk, Listbox, Menu, END, ACTIVE, W, E
from ttk import Frame, LabelFrame, Button, Entry


class Controller(Thread):
    """
    Dedicated thread for the GUI.
    """
    def __init__(self, searcher):
        """
        Create a Controller thread, connected
        to the given Searcher.
        """
        Thread.__init__(self, name='Controller')
        self.searcher = searcher

    def run(self):
        """
        Starts up and runs the GUI. Closes Tweeteor
        once the GUI is closed.
        """
        try:
            root = Tk()
            app = GUI(self.searcher, master=root)
            app.mainloop()
            self.searcher.exit.set()
        except:
            # This block does not actually handle the error, only log it.
            # That's why we re-raise the error, so that important errors
            # are not silenced.
            logging.exception("Fatal Exception Thrown")
            raise


class GUI(Frame):
    """
    The window for the controller GUI. Contains the Frames
    and Buttons used by the user.
    """

    def __init__(self, searcher, master=None):
        """
        Creates a window with a quit button and a ListFrame
        for each search term list, all linked to the given searcher.
        """
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
    """
    A Frame representing one of the search term lists
    (e.g. Hashtags, Excluded Users).

    Displays all the items in the list,
    and allows the user to add or remove items.
    Methods should not be called directly;
    instead they should be bound as event handlers.
    """

    def __init__(self, name, add_handler, remove_handler, master=None):
        """
        Creates a ListFrame with the given name as its title.

        add_handler and remove_handler are functions to be called
        when items are added or removed, and should relay the information
        back to the Searcher (or whatever object actually uses the list).
        """
        LabelFrame.__init__(self, master)
        self['text'] = name
        self.add_handler = add_handler
        self.remove_handler = remove_handler
        self.list = Listbox(self)
        self.list.grid(row=0, columnspan=2)
        # Tkinter does not automatically close the right-click menu for us,
        # so we must close it when the user clicks away from the menu.
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
        # Tkinter passes an event object to the add method,
        # so it must be a parameter even though we don't use it.
        """
        Add the item in the input line to the list.
        """
        self.list.insert(END, self.input.get())
        self.add_handler(self.input.get())
        self.input.delete(0, END)

    def remove(self):
        """
        Remove the active (highlighted) item from the list.
        """
        deleted = self.list.get(ACTIVE)
        self.list.delete(ACTIVE)
        self.remove_handler(deleted)

    def open_menu(self, event):
        """
        Opens a right-click menu for the selected item.
        Currently the menu only has an option for removing the item.
        """
        index = self.list.index("@" + str(event.x) + "," + str(event.y))
        if index < 0:
            return
        self.context_menu.post(event.x_root, event.y_root)
        self.list.activate(index)
        self.list.selection_clear(0, END)
        self.list.selection_set(ACTIVE)
