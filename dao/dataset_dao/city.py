from .cell import Cell
from .utils import get_city_state_at_time, get_weather, get_events, get_predict
from model.dataset import TaxiBJDataset
from model.eval import dataset


class City:
    def __init__(self, time, predict_mode=False):
        self.structure = []
        self.time = time
        self.predict_mode = predict_mode
        inf, outf = get_city_state_at_time(time)
        map_size = 32
        self.weather = get_weather(time)
        self.holiday = get_events(time)

        if self.predict_mode:
            self.predict_structure = []
            predict_data = get_predict(dataset, time)
            self.rmse = predict_data['rmse']

        number = 0

        for i in range(map_size):
            for j in range(map_size):
                # print(f'i = {i}   j = {j}')
                # print(f'number {number}')
                cell = Cell(number, inf[j][i], outf[j][i])
                self.structure.append(cell)
                if self.predict_mode:
                    cell = Cell(number, predict_data['inflow'][j][i], predict_data['outflow'][j][i])
                    self.predict_structure.append(cell)
                number += 1

    def get_cell_from_city(self, number):
        cell = self.structure[number]
        return

    def get_city_state(self):
        inflows = []
        outflows = []
        for cell in self.structure:
            state = cell.get_state()
            inflows.append(state[0])
            outflows.append(state[1])
        return inflows, outflows

    def get_city_predict_state(self):
        inflows = []
        outflows = []
        for cell in self.predict_structure:
            state = cell.get_state()
            inflows.append(state[0])
            outflows.append(state[1])
        return inflows, outflows

    def get_city_weather(self):
        return self.weather

    def check_holiday(self):
        return self.holiday

    def get_rmse(self):
        return self.rmse