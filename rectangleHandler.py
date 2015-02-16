import pygame, json, tweet

#Helper method for placing surfaces on a larger surface
def blitList(surface, sourceList, boundary = 0):
        loc = [0, 0]
        addedList = []#List of all surfaces in current column
        for source in sourceList:
                if loc[1] + source.get_height() > surface.get_height():#Starts new column if surfaces reach bottom of the destination surface
                        loc[1] = 0
                        loc[0] += max([s.get_width() for s in addedList])#Only make the columns as wide as needed
                        addedList = []
		if loc[0] + source.get_width() > surface.get_width():#Ignores surfaces too wide to fit in the surface, you don't want ugly half surfaces
			continue
		if boundary > 0 and (loc[1] + source.get_height()) / boundary != loc[1] / boundary:
			loc[1] += boundary - loc[1] % boundary
                surface.blit(source, loc)
                loc[1] += source.get_height()#move down a "row"
                addedList.append(source)

def positionSurfaces(surface, sourceList, boundary = 0):
        loc = [0, 0]
        addedList = []#List of all surfaces in current column
        for source in sourceList:
                if loc[1] + source.get_height() > surface.get_height():#Starts new column if surfaces reach bottom of the destination surface
                        loc[1] = 0
                        loc[0] += max([s.get_width() for s in addedList])#Only make the columns as wide as needed
                        addedList = []
		if loc[0] + source.get_width() > surface.get_width():#Ignores surfaces too wide to fit in the surface, you don't want ugly half surfaces
			continue
		if boundary > 0 and (loc[1] + source.get_height()) / boundary != loc[1] / boundary:
			loc[1] += boundary - loc[1] % boundary
                surface.blit(source, loc)
                loc[1] += source.get_height()#move down a "row"
                addedList.append(source)


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
