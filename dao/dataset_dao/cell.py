from .utils import get_some_shots_for_cell, get_predict_for_cell
from model.dataset import TaxiBJDataset
from model.eval import dataset

class Cell:
    def __init__(self, id, inf, outf):
        self.id = id
        if inf is None or outf is None:
            self.inflows = []
            self.inflows = []
        else:
            self.inf = int(inf)
            self.outf = int(outf)

    def get_state(self):
        return [self.inf, self.outf]

    def get_daily_state(self, datetime, depth):
        return get_some_shots_for_cell(datetime, self.id, depth)

    def get_predict_state(self, datetime):
        return get_predict_for_cell(datetime, self.id, dataset)
