import sys
import random
import itertools
import numpy as np
import cv2 as cv

MAP_FILE = "cape_python.png"

SA1_CORNERS = (130, 265, 180, 315) #(LT X, LT Y, RB X, RB Y)
SA2_CORNERS = (80, 255, 130, 305) #(LT X, LT Y, RB X, RB Y)
SA3_CORNERS = (105, 205, 155, 255) #(LT X, LT Y, RB X, RB Y)

class Search():
    """
    A Bayesian game for simulating a search and rescue mission with 
    three search areas.
    """

    def __init__(self, name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        
        if self.img is None:
            print("Can't load map image file {}".format(MAP_FILE), file=sys.stderr)
            sys.exit(1)
        
        self.area_actual = 0
        self.sailor_actial = [0, 0]

        #Local coordinates in the search area
        self.sa1 = self.img[SA1_CORNERS[1] : SA1_CORNERS[3],
                            SA1_CORNERS[0] : SA1_CORNERS[2]]
        
        self.sa2 = self.img[SA2_CORNERS[1] : SA2_CORNERS[3],
                            SA2_CORNERS[0] : SA2_CORNERS[2]]
        
        self.sa3 = self.img[SA3_CORNERS[1] : SA3_CORNERS[3],
                            SA3_CORNERS[0] : SA3_CORNERS[2]]
        
        #Propability of finding a sailor in subsequent search areas from SAROPS
        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

        #Propability of search effectiveness in subsequent search areas
        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0
    
    def draw_map(self, last_known):
        """
        Draws a region map with a scale, last know location and search areas. 
        """
        cv.line(self.img, (20, 370), (70, 370), (0, 0, 0), 2)
        cv.putText(self.img, '0', (8, 370), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv.putText(self.img, '50 nautical miles', (71, 370), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
        cv.rectangle(self.img, (SA1_CORNERS[0], SA1_CORNERS[1]), (SA1_CORNERS[2], SA1_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '1', (SA1_CORNERS[0] + 3, SA1_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA2_CORNERS[0], SA2_CORNERS[1]), (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '2', (SA2_CORNERS[0] + 3, SA2_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.rectangle(self.img, (SA3_CORNERS[0], SA3_CORNERS[1]), (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)
        cv.putText(self.img, '3', (SA3_CORNERS[0] + 3, SA3_CORNERS[1] + 15), cv.FONT_HERSHEY_PLAIN, 1, 0)
        cv.putText(self.img, '+', last_known, cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '+ = last known location', (240, 355), cv.FONT_HERSHEY_PLAIN, 1, (0, 0, 255))
        cv.putText(self.img, '* = actual location', (242, 370), cv.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

        cv.imshow('Areas to search', self.img)
        cv.moveWindow('Areas to search', 750, 10)
        cv.waitKey(500)

def main():
    app = Search("Bayes")
    app.draw_map((50, 30))

if __name__ == '__main__':
    main()


