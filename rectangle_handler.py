"""
Miscellaneous functions for dealing with rectangles.
"""
import pygame


def make_column(surfaces, bg_color):
    """
    Make a surface containing the given surfaces in a column,
    with the bg_color as the background color.
    """
    width = max([o.get_width() for o in surfaces])
    height = sum([o.get_height() for o in surfaces])
    destination = pygame.Surface((width, height))
    destination.fill(bg_color)
    blit_list(surfaces, destination)
    return destination


def make_row(surfaces, bg_color):
    """
    Make a surface containing the given surfaces in a row,
    with the bg_color as the background color.
    """
    width = sum([o.get_width() for o in surfaces])
    height = max([o.get_height() for o in surfaces])
    destination = pygame.Surface((width, height))
    destination.fill(bg_color)
    blit_list(surfaces, destination)
    return destination

def make_header(surfaces, bg_color, total_width):
    height = max([o.get_height() for o in surfaces])
    width = sum([o.get_width() for o in surfaces])

    img = surfaces[0]
    img_rect = img.get_rect()

    screenname = surfaces[1]
    screenname_rect = screenname.get_rect()

    img_rect.x = (total_width - width)/2
    screenname_rect.x = img_rect.x + img_rect.width
    screenname_rect.y = (height - screenname_rect.height)/2

    sources = []
    sources.append((img, img_rect))
    sources.append((screenname, screenname_rect))

    destination = pygame.Surface((total_width, height))
    destination.fill(bg_color)

    for (source, rect) in sources:
        destination.blit(source, rect)
    return destination


def blit_list(sources, destination):
    """
    Blit all surfaces in sources onto destination.

    Surfaces are blitted top to bottom, left to right.
    """
    sources = position_rectangles(sources, destination)
    for (source, rect) in sources:
        destination.blit(source, rect)


def position_rectangles(objects, surface):
    """
    Position objects so that they can fit onto a surface.
    Returns a list of (source, rectangle) pairs, but also
    updates the source's rectangle attribute if possible.

    Objects are placed top to bottom, left to right. Works
    on all objects that have a get_rect() method, not just surfaces.
    """
    x = 0
    y = 0
    column = []
    output = []
    for o in objects:
        rect = o.get_rect()
        if y + rect.height > surface.get_height():
            y = 0
            x += max([r.width for r in column])
            column = []
        rect.x = x
        rect.y = y
        y += rect.height
        column.append(rect)
        if hasattr(o, 'rect'):
            o.rect = rect
        output.append((o, rect))
    return output
