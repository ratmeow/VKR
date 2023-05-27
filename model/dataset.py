from torch.utils import data
from preprocessing.loadTaxiBJ import load_data
from preprocessing.new_load import load_data_mode, extract_test

class TaxiBJDataset(data.Dataset):

    def __init__(self, mode, len_c, len_p, len_t, len_test):
        self.mode = mode
        self.len_c = len_c
        self.len_p = len_p
        self.len_t = len_t
        self.len_test = len_test

        if self.mode == 'train':
            print("Loading TaxiBJ data to create train set...\n")
            # X_data Shape
            self.X_data, self.Y_data, _, _, mmn, metadata_dim, timestamp_train, timestamp_test = load_data(
                len_closeness=self.len_c,
                len_period=self.len_p,
                len_trend=len_t,
                len_test=len_test
            )
        elif self.mode == 'test':
            print("Loading TaxiBJ data to create test set...\n")
            self.XC, self.XP, self.XT, self.Y, self.mmn, self.metadata_dim, self.timestamps_Y, self.meta_feature = load_data_mode(len_closeness=self.len_c,
                                                                            len_period=self.len_p, len_trend=len_t)
            print(self.timestamps_Y)
            print(len(self.timestamps_Y))
        else:
            print("Error: Unknown dataset mode!")
            assert 0



    def __getitem__(self, item):
        X_c, X_p, X_t, X_meta = self.X_data[0][item], self.X_data[1][item], \
                                self.X_data[2][item], self.X_data[3][item]
        y = self.Y_data[item]
        return X_c, X_p, X_t, X_meta, y

    def __len__(self):
        return self.data_len


    def set_test(self, start, end):
        self.X_data, self.Y_data, timestamp_test = extract_test(start, end, self.XC, self.XP, self.XT, self.Y, self.timestamps_Y,
                                                                self.meta_feature)
        assert len(self.X_data[0]) == len(self.Y_data)
        self.data_len = len(self.Y_data)

# if __name__ == '__main__':
#     taxi_bj = TaxiBJDataset(mode='train', len_c=3, len_p=1, len_t=1, len_test=28*48)


