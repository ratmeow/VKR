from model.dataset import TaxiBJDataset
from model.STResNet import STResNet
from torch.utils.data import DataLoader
from utils.mertics import RMSELoss, MAPELoss
import torch
import numpy as np
import time


"""
parameter setting
"""
l_c = 3
l_p = 1
l_t = 1
# flow_dim = 2
# map_height = 32
# map_width = 32

T = 1
days_test = 1
len_test = T * days_test
batch_size = 1
gpu_id = 0
device = torch.device('cpu')
rmse = RMSELoss().to(gpu_id)
mape = MAPELoss().to(gpu_id)
dataset = TaxiBJDataset(mode='test', len_c=l_c, len_p=l_p, len_t=l_t, len_test=len_test)
model = STResNet(lc=l_c, lp=l_p, lt=l_t).to(device)
model.load('checkpoints/done_models/STResNet_L12_E50.pth')
model.eval()

def rescale_loss(mmn, y, y_pred):
    y_pred = mmn.inverse_transform(y_pred)
    y = mmn.inverse_transform(y)
    rescale_rmse = rmse(y, y_pred)
    rescale_mape = mape(y, y_pred)
    return y_pred, y, rescale_rmse, rescale_mape


def evaluate(test_dataset, start, end, model,cell_mode=False):
    test_dataset.set_test(start, end)
    mmn = test_dataset.mmn
    test_data_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    y_list = []
    y_pred_list = []
    rmse_list = []
    mape_list = []
    for batch_idx, (X_c, X_p, X_t, X_meta, Y_batch) in enumerate(test_data_loader):
        X_c = X_c.type(torch.FloatTensor).to(device)
        X_p = X_p.type(torch.FloatTensor).to(device)
        X_t = X_t.type(torch.FloatTensor).to(device)
        X_meta = X_meta.type(torch.FloatTensor).to(device)
        Y_batch = Y_batch.type(torch.FloatTensor).to(device)
        outputs = model(X_c, X_p, X_t, X_meta)
        y_pred, y, rmse_loss, mape_loss = rescale_loss(mmn=mmn, y=Y_batch, y_pred=outputs)
        y_list.append(y)
        y_pred_list.append(y_pred)
        rmse_list.append(rmse_loss.item())
        mape_list.append(mape_loss.item())
    if cell_mode:
        return y_pred_list
    return y_pred_list[-1], np.mean(rmse_list), np.mean(mape_list)




    # print('[Test] RMSE: ', np.mean(test_rmse), ' MAPE: ', np.mean(test_mape))


if __name__ == '__main__':
    # train()
    start = time.time()
    evaluate()
    end = time.time()
    print(end - start)