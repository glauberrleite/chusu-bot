import json
import numpy as np
from datetime import date


class Chusu:

    def __init__(self, chusu_size):
        self.chusu = np.zeros((3,3))
        self.trays_list = []

    def new_Tray(self):
        # searching for an empty space for a new tray
        empty_tray = np.where(self.chusu_trays == 0)
        tray_index = list(zip(tray_index[0],tray_index[1]))
        
        # initiating a new Tray 
        # after creating needs to update
        tray = Tray(self.chusu.size + 1, tray_index[0], 0,0)
        self.trays_list.append(tray)

        #updating cell status
        self.chusu_trays[tray_index[0][0]][tray_index[0][1]] = 1

    def update_status(self):
        for tray in self.trays_list:
            tray.update_sensors()

    def remove_tray(self, tray_id):
        #remove tray by id
        #status in the matrix will be updated to 0
        return

    def central_server_update(self, tray):
        
        
        
        
        return

class Tray:
    
    def __init__(self, coodinates, cell, color, radius):
        self.id = id
        self.coordinates = coodinates
        self.color = color
        self.radius = radius
        self.time = date.today()
        self.havest_score = 0

    def update_sensors(self):
        #here some magic happens
        #color, radius and havest_score are updated
        #updated_time = date.today() - time
        #self.havest_score = self.Havest(updated_color, updated_radius, updated_time)
        return

    def Havest(self, color, radius, time):
        w_c = 0.2 
        w_r = 0.3
        w_t = 0.5
        return w_c*pow(color, -1) + w_r*radius + w_t*time

