import sys
import random
import itertools
import numpy as np
import cv2 as cv

MAP_FILE = 'cape_python.png'

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
        
        #Actual location of the sailor
        self.area_actual = 0
        self.sailor_actual = [0, 0]

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

        #Stores searched coords for each area in 2d array
        self.searched_coords = [[], [], []]
    
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
        cv.moveWindow('Areas to search', 1300, 100)
        cv.waitKey(500)

    def sailor_final_location(self, num_search_areas):
        """Returns coordinates x and y of actual location of the sailor"""
        #Finds coordinates of the sailor relative to the search area subarray
        self.sailor_actual[0] = np.random.choice(self.sa1.shape[1], 1)
        self.sailor_actual[1] = np.random.choice(self.sa1.shape[0], 1)

        area = int(random.triangular(1, num_search_areas + 1))
    
        if area == 1:
            x = self.sailor_actual[0] + SA1_CORNERS[0]
            y = self.sailor_actual[1] + SA1_CORNERS[1]
            self.area_actual = 1
        elif area == 2:
            x = self.sailor_actual[0] + SA2_CORNERS[0]
            y = self.sailor_actual[1] + SA2_CORNERS[1]
            self.area_actual = 2
        elif area == 3:
            x = self.sailor_actual[0] + SA3_CORNERS[0]
            y = self.sailor_actual[1] + SA3_CORNERS[1]
            self.area_actual = 3
        
        
        return x, y

    def calc_search_effectiveness(self):
        """
        Specifies a decimal value representing search effectiveness for each area
        """
        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2, 0.9)
        self.sep3 = random.uniform(0.2, 0.9)

    def conduct_search(self, area_num, area_array, effectiveness_prob):
        """Returns result of search and list of search coordinates"""
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])
        coords = list(itertools.product(local_x_range, local_y_range))
        #Deleting already searched coordinates from list of all coordinates
        for cord in coords:
            for searched_coord in self.searched_coords[area_num-1]:
                if cord == searched_coord:
                    coords.remove(cord)

        random.shuffle(coords)
        coords = coords[:int((len(coords) * effectiveness_prob))]
        
        #Storing already searched coordinates
        self.searched_coords[area_num-1] = list(set(self.searched_coords[area_num-1] + coords))

        loc_actual = (self.sailor_actual[0], self.sailor_actual[1])
        if area_num == self.area_actual and loc_actual in coords:
            return 'Found in area number {}.'.format(area_num), coords
        else:
            return 'Not found', coords
        
    def revise_target_probs(self):
        """
        Updates propability for each area based on search effectiveness
        """
        denom = self.p1 * (1 - self.sep1) + self.p2 * (1 - self.sep2) + self.p3 * (1 - self.sep3)
        self.p1 = self.p1 * (1 - self.sep1) / denom
        self.p2 = self.p2 * (1 - self.sep2) / denom
        self.p3 = self.p3 * (1 - self.sep3) / denom

    def _draw_menu(self, search_num):
        """Prints the menu with the selection of area to be searched""" 
        print('Attempt number {}'.format(search_num))

        print(
            """
            Choose next area to search:

            0 - Exit the program
            1 - Search first area twice
            2 - Search second area twice
            3 - Search third area twice
            4 - Search first and second area
            5 - Search first and third area
            6 - Search second and third area
            7 - Start from beggining
            """

        )

    def run_game(self):
        self.draw_map(last_known=(160, 290))
        
        sailor_x, sailor_y = self.sailor_final_location(num_search_areas=3)
        print("-" * 65)
        print("\nInitial probability estimate (P):")
        print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}".format(self.p1, self.p2, self.p3))
        search_num = 1

        while True:
            self.calc_search_effectiveness()
            self._draw_menu(search_num)
            choice = input("Choose an option: ")

            if choice == "0":
                sys.exit()

            elif choice == "1":
                results_1, coords_1 = self.conduct_search(1, self.sa1, self.sep1)
                results_2, coords_2 = self.conduct_search(1, self.sa1, self.sep1)
                self.sep1 = (len(set(coords_1 + coords_2))) / (len(self.sa1) ** 2)
                self.sep2 = 0
                self.sep3 = 0

            elif choice == "2":
                results_1, coords_1 = self.conduct_search(2, self.sa2, self.sep2)
                results_2, coords_2 = self.conduct_search(2, self.sa2, self.sep2)
                self.sep1 = 0
                self.sep2 = (len(set(coords_1 + coords_2))) / (len(self.sa2) ** 2)
                self.sep3 = 0

            elif choice == "3":
                results_1, coords_1 = self.conduct_search(3, self.sa3, self.sep3)
                results_2, coords_2 = self.conduct_search(3, self.sa3, self.sep3)
                self.sep1 = 0
                self.sep2 = 0
                self.sep3 = (len(set(coords_1 + coords_2))) / (len(self.sa3) ** 2)

            elif choice == "4":
                results_1, coords_1 = self.conduct_search(1, self.sa1, self.sep1)
                results_2, coords_2 = self.conduct_search(2, self.sa2, self.sep2)
                self.sep3 = 0

            elif choice == "5":
                results_1, coords_1 = self.conduct_search(1, self.sa1, self.sep1)
                results_2, coords_2 = self.conduct_search(3, self.sa3, self.sep3)
                self.sep2 = 0

            elif choice == "6":
                results_1, coords_1 = self.conduct_search(2, self.sa2, self.sep2)
                results_2, coords_2 = self.conduct_search(3, self.sa3, self.sep3)
                self.sep1 = 0

            elif choice == "7":
                main()

            else:
                print("\nIt is not correct choice.", file=sys.stderr)
                continue
            
            #Uses Bayes Theorem to update probability
            self.revise_target_probs()

            print("\nAttempt number {} - result: {}".format(search_num, results_1), file=sys.stderr)
            print("\nAttempt number {} - result: {}".format(search_num, results_2), file=sys.stderr)
            print("Search effectiveness (E) for attempt number {}:".format(search_num))
            print("E1 = {:.3f}, E2 = {:.3f}, E3 = {:.3f}".format(self.sep1, self.sep2, self.sep3))

            if results_1 == 'Not found' and results_2 == 'Not found':
                print("\nNew probability estimate: (P) " "for attempt number {}:".format(search_num + 1))
                print("P1 = {:.3f}, P2 = {:.3f}, P3 = {:.3f}".format(self.p1, self.p2, self.p3))
            else:
                cv.circle(self.img, (sailor_x[0], sailor_y[0]), 3, (255, 0, 0), -1)
                cv.imshow('Areas to search', self.img)
                cv.waitKey(5000)
                main()
            search_num += 1

def main():
    app = Search('Cape_Python')
    app.run_game()
    

if __name__ == '__main__':
    main()


