import json
import numpy as np
import pandas as pd 
from datetime import date
from time import sleep

class Chusu:

    def __init__(self, chusu_size):
        self.chusu = np.zeros((3,3))
        self.trays_list = []
        self.luminous = "780lx"
        self.temperature = "28°C"
        self.humidity = "70%"
    
    def new_Tray(self):
        if len(self.trays_list) < self.chusu.size:
                
            # searching for an empty space for a new tray
            empty_tray = np.where(self.chusu_trays == 0)
            tray_index = list(zip(tray_index[0],tray_index[1]))
            
            # initiating a new Tray 
            # after creating needs to update
            tray = Tray(self.chusu.size - len(self.trays_list), tray_index[0], 0,0)
            self.trays_list.append(tray)

            #updating cell status
            self.chusu_trays[tray_index[0][0]][tray_index[0][1]] = 1
        else:
            print("Chusu it's already full, choose another one")

    def update_status(self):
        #self.update_tray_status()
        print(self.temperature + self.humidity + self.luminous)

    def update_tray_status(self):
        for tray in self.trays_list:
            tray.update_sensors()
        print(tray.id + tray.color + tray.radius + tray.havest_score + tray.time)

    def remove_tray(self, tray_id):
        #remove tray by id
        #status in the matrix will be updated to 0
        return

    def central_server_update(self):
    
    #    chusu_data = {
    #        'id': tray.id, 
    #        'coordinates': tray.coordinates,
    #        'color': tray.color,
    #        'radius': tray.radius,
    #        'time': tray.time,
    #        'havest_score': tray.havest_score
    #    }
    
        chusu_data_frame = pd.DataFrame(columns=['id', 
                                                'coordinates',
                                                'color',
                                                'radius',
                                                'time',
                                                'havest_score'])

        for tray in self.trays_list:
            chusu_data_frame.loc[tray] = [tray.id + 
                                        tray.coordinates +
                                        tray.color +
                                        tray.radius +
                                        tray.time +
                                        tray.havest_score]

        chusu_data_frame.to_csv('chusu_sensors_update.csv', float_format='%.2f')


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
        updated_time = date.today() - time
        self.havest_score = self.Havest(np.random.randint(255), np.random().rand() + np.random.randint(5), updated_time)

    def Havest(self, color, radius, time):
        w_c = 0.2 
        w_r = 0.3
        w_t = 0.5
        return w_c*pow(color, -1) + w_r*radius + w_t*time



if __name__ == "__main__":

    chusinho = Chusu(3)
    chusinho.new_Tray()
    chusinho.update_tray_status()

    while(True):
        chusinho.update_status()
        sleep(10)
        chusinho.update_tray_status()
        sleep(10)
        chusinho.central_server_update()
        sleep(30)

