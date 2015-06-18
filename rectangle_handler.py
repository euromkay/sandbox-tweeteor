"""
Miscellaneous functions for dealing with rectangles.
Should be broken into multiple modules.
"""
import json
import pygame
import tweet


def blit_list(sources, destination):
    """
    Blit all surfaces in sources onto destination.

    Surfaces are blitted top to bottom, left to right.
    """
    sources = position_rectangles(sources, destination)
    for (source, rect) in sources:
        destination.blit(source, rect)


def position_rectangles(source_list, surface):
    """
    Position objects so that they can fit onto a surface.
    Returns a list of (source, rectangle) pairs, but also
    updates the source's rectangle attribute if possible.

    Objects are placed top to bottom, left to right. Works
    on all objects that have a get_rect() method, not just surfaces.
    """
    x = 0
    y = 0
    added_list = []  # List of all rectangles in current column
    sources = []  # tuples containing sources and their rectangles
    for source in source_list:
        rect = source.get_rect()
        # Starts new column if rectanges reach bottom
        # of the destination surface
        if y + rect.height > surface.get_height():
            y = 0
            # Only make the columns as wide as needed
            x += max([r.width for r in added_list])
            added_list = []
        rect.x = x
        rect.y = y
        y += rect.height  # move down a "row"
        added_list.append(rect)
        if hasattr(source, 'rect'):
            source.rect = rect
        sources.append((source, rect))
    return sources


class RectangleEncoder(json.JSONEncoder):
    """Encodes both Tweet objects and pygame Rects into JSON."""

    def __init__(self):
        json.JSONEncoder.__init__(self)

    def default(self, o):
        if isinstance(o, pygame.Rect):
            x = {'left': o.left,
                 'top': o.top,
                 'width': o.width,
                 'height': o.height,
                 'class': "Rect"}
        elif isinstance(o, tweet.Tweet):
            x = o.__dict__
            x['class'] = 'Tweet'
        else:
            x = json.JSONEncoder.default(self, o)
        return x


def decode_object(dictionary):
    """
    Decodes JSON into Pygame Rects and Tweet Objects (as long as they
    were encoded with RectangleEncoder).
    """
    if 'class' in dictionary:
        if dictionary['class'] == 'Tweet':
            return tweet.Tweet(
                dictionary['json'],
                decode_object(dictionary['rect']))
        if dictionary['class'] == 'Rect':
            return pygame.Rect(
                dictionary['left'],
                dictionary['top'],
                dictionary['width'],
                dictionary['height'])
    return dictionary
