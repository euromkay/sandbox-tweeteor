import pygame

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
