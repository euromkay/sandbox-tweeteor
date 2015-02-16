import pygame, json, tweet

#Helper method for placing surfaces on a larger surface
def blitList(surface, sourceList, boundary = 0):
        sources = positionRectangles(surface, sourceList, boundary)
        for (source, rect) in sources:
            surface.blit(source, rect)

#Positions any object with a get_rect() method, so they can be blitted
def positionRectangles(surface, sourceList, boundary = 0):
        x = 0
        y = 0
        addedList = []#List of all rectangles in current column
        sources = [] #tuples containing sources and their rectangles
        for source in sourceList:
                rect = source.get_rect()
                if y + rect.height > surface.get_height():#Starts new column if rectanges reach bottom of the destination surface
                        y = 0
                        x += max([r.width for r in addedList])#Only make the columns as wide as needed
                        addedList = []
		if boundary > 0 and (y + rect.height) / boundary != y / boundary:
			y += boundary - y % boundary
                rect.x = x
                rect.y = y
                y += rect.height#move down a "row"
                addedList.append(rect)
                sources.append((source, rect))
        return sources


class RectangleEncoder(json.JSONEncoder):
    def __init__(self):
        json.JSONEncoder.__init__(self)
    def default(self, o):
        if isinstance(o, pygame.Rect):
            o = {'left': o.left, 'top': o.top, 'width': o.width, 'height': o.height, 'class': "Rect"}
        elif isinstance(o, tweet.Tweet):
            o = o.__dict__
            o['class'] = 'Tweet'
        else:
            return json.JSONEncoder.default(self, o)
        return o

def decodeObject(dictionary):
    if 'class' in dictionary:
        if dictionary['class'] == 'Tweet':
            return tweet.Tweet(dictionary['json'], dictionary['height'], dictionary['width']) 
        if dictionary['class'] == 'Rect':
            return pygame.Rect(dictionary['left'], dictionary['top'], dictionary['width'], dictionary['height']) 
    return dictionary
