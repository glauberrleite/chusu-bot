import numpy as np
from datetime import date

class Tray:
    
    def __init__(self, id, coordinates, color, radius):
        self.id = id
        self.coordinates = coordinates
        self.color = color
        self.radius = radius
        self.time = date.today()
        self.havest_score = 0

    def update_sensors(self):
        #here some magic happens
        #color, radius and havest_score are updated
        #updated_time = date.today() - time
        #self.havest_score = self.Havest(updated_color, updated_radius, updated_time)
        updated_time = date.today() - self.time
        self.havest_score = self.Havest(np.random.randint(255), np.random().rand() + np.random.randint(5), updated_time)

    def Havest(self, color, radius, time):
        w_c = 0.2 
        w_r = 0.3
        w_t = 0.5
        return w_c*pow(color, -1) + w_r*radius + w_t*time
