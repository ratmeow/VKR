import os
import numpy as np
import h5py
import time
import pickle
from preprocessing.st_matrix import STMatrix
from utils.timestamp_tools import timestamp2vec
from utils.normalization import MinMaxNormalization

DATAPATH = 'R:/vkr2/fastapi/dao/TaxiBJ'
# CACHEPATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'checkpoints')
MMN_FILE = 'checkpoints/min_max_model.pkl'


def load_holiday(timeslots, fname=os.path.join(DATAPATH, 'BJ_Holiday.txt')):
    f = open(fname, 'r')
    holidays = f.readlines()
    holidays = set([h.strip() for h in holidays])
    # print(holidays)
    H = np.zeros(len(timeslots))
    for i, slot in enumerate(timeslots):
        if slot[:8] in holidays:
            H[i] = 1
    # print(H.sum())
    return H[:, None]


def load_meteorology(timeslots, fname=os.path.join(DATAPATH, 'BJ_Meteorology.h5')):
    f = h5py.File(fname, 'r')
    Timeslot = f['date'][()]
    WindSpeed = f['WindSpeed'][()]
    Weather = f['Weather'][()]
    Temperature = f['Temperature'][()]
    f.close()

    M = dict()  # map timeslot to index
    for i, slot in enumerate(Timeslot):
        M[slot] = i

    WS = []  # WindSpeed
    WR = []  # Weather
    TE = []  # Temperature
    for slot in timeslots:
        predicted_id = M[slot]
        cur_id = predicted_id - 1
        WS.append(WindSpeed[cur_id])
        WR.append(Weather[cur_id])
        TE.append(Temperature[cur_id])

    WS = np.asarray(WS)
    WR = np.asarray(WR)
    TE = np.asarray(TE)

    # 0-1 scale
    WS = 1. * (WS - WS.min()) / (WS.max() - WS.min())
    TE = 1. * (TE - TE.min()) / (TE.max() - TE.min())

    # print("shape: ", WS.shape, WR.shape, TE.shape)

    # concatenate all these attributes
    merge_data = np.hstack([WR, WS[:, None], TE[:, None]])

    # print('meger shape:', merge_data.shape)
    return merge_data


def data_statistics(fname):
    """
    Return data information like the following

    data shape: (7220, 2, 32, 32)
    # of days: 162, from 2015-11-01 to 2016-04-10
    # of timeslots: 7776
    # of timeslots (available): 7220
    missing ratio of timeslots: 7.2%
    max: 1250.000, min: 0.000
    """

    def count_timeslot(f):
        """
        count the number of timeslot of given data

        time slot format:
        ****,**,**,** --> year, month, day, interval
        """
        start_slot = f['date'][0]
        end_slot = f['date'][-1]
        year, month, day = map(int, [start_slot[:4], start_slot[4:6], start_slot[6:8]])
        start_date = time.strptime("%04i-%02i-%02i" % (year, month, day), "%Y-%m-%d")
        year, month, day = map(int, [end_slot[:4], end_slot[4:6], end_slot[6:8]])
        end_date = time.strptime("%04i-%02i-%02i" % (year, month, day), "%Y-%m-%d")
        timeslot_num = (time.mktime(end_date) - time.mktime(start_date)) / (0.5 * 3600) + 48  # interval=30min
        start_date_str, end_date_str = time.strftime("%Y-%m-%d", start_date), time.strftime("%Y-%m-%d", end_date)
        return timeslot_num, start_date_str, end_date_str

    with h5py.File(fname, 'r') as f:
        timeslot_num, start_date_str, end_date_str = count_timeslot(f)
        day_num = int(timeslot_num / 48)
        max_value = f['data'][()].max()
        min_value = f['data'][()].min()
        stat = '=' * 10 + 'statistical info' + '=' * 10 + '\n' + \
               'data shape: %s\n' % str(f['data'].shape) + \
               '# of days: %i, from %s to %s\n' % (day_num, start_date_str, end_date_str) + \
               '# of timeslots: %i\n' % int(timeslot_num) + \
               '# of timeslots (available): %i\n' % f['date'].shape[0] + \
               'missing ratio of timeslots: %.1f%%\n' % ((1. - float(f['date'].shape[0] / timeslot_num)) * 100) + \
               'max: %.3f, min: %.3f\n' % (max_value, min_value) + \
               '=' * 10 + 'statistical info' + '=' * 10
        print(stat)


def load_st_data(fname):
    f = h5py.File(fname, 'r')
    data = f['data'][()]
    timestamps = f['date'][()]
    f.close()
    return data, timestamps


def remove_incomplete_days(data, timestamps, T=48):
    """
    remove a certain day which has not 48 timestamps
    """
    days = []  # available days: some day only contain some seqs
    days_incomplete = []
    i = 0
    while i < len(timestamps):
        if int(timestamps[i][8:]) != 1:
            i += 1
        elif i + T - 1 < len(timestamps) and int(timestamps[i + T - 1][8:]) == T:
            days.append(timestamps[i][:8])
            i += T
        else:
            days_incomplete.append(timestamps[i][:8])
            i += 1
    print("incomplete days: ", days_incomplete)
    days = set(days)
    idx = []
    for i, t in enumerate(timestamps):
        if t[:8] in days:
            idx.append(i)

    data = data[idx]
    timestamps = [timestamps[i] for i in idx]
    return data, timestamps


def load_data_mode(T=48, flow_channel=2, len_closeness=None, len_period=None, len_trend=None,
              meta_data=True, meteorology_data=True, holiday_data=True):
    assert (len_closeness + len_period + len_trend > 0)
    year = 16
    fname = os.path.join(DATAPATH, 'BJ{}_M32x32_T30_InOut.h5'.format(year))
    print("file name: ", fname)
    # data_statistics(fname)
    data, timestamps = load_st_data(fname)
    data, timestamps = remove_incomplete_days(data, timestamps, T)
    data = data[:, :flow_channel]
    data[data < 0] = 0.

    print('Execute Min-Max Scale...')
    with open(MMN_FILE, 'rb') as fpkl:
        mmn = pickle.load(fpkl)
    data_all_mmn = [mmn.transform(d) for d in data]

    XC, XP, XT = [], [], []
    Y = []
    timestamps_Y = []

    st = STMatrix(data_all_mmn, timestamps, T, CheckComplete=False)
    _XC, _XP, _XT, _Y, _timestamps_Y = st.create_dataset(
        len_closeness=len_closeness, len_period=len_period, len_trend=len_trend)
    XC.append(_XC)
    XP.append(_XP)
    XT.append(_XT)
    Y.append(_Y)
    timestamps_Y += _timestamps_Y

    print(timestamps_Y)

    meta_feature = []
    if meta_data:
        # load time feature
        time_feature = timestamp2vec(timestamps_Y)
        meta_feature.append(time_feature)
    if holiday_data:
        # load holiday
        holiday_feature = load_holiday(timestamps_Y)
        meta_feature.append(holiday_feature)
    if meteorology_data:
        # load meteorology data
        meteorology_feature = load_meteorology(timestamps_Y)
        meta_feature.append(meteorology_feature)

    meta_feature = np.hstack(meta_feature) if len(meta_feature) > 0 else np.asarray(meta_feature)

    metadata_dim = meta_feature.shape[1] if len(meta_feature.shape) > 1 else None

    if metadata_dim < 1:
        metadata_dim = None


    XC = np.vstack(XC)
    XP = np.vstack(XP)
    XT = np.vstack(XT)
    Y = np.vstack(Y)

    return XC, XP, XT, Y, mmn, metadata_dim, timestamps_Y, meta_feature


def extract_test(start, end, XC, XP, XT, Y, timestamps_Y, meta_feature):
    XC_test, XP_test, XT_test, Y_test = XC[start+1:end+1], XP[start+1:end+1], XT[start+1:end+1], Y[start+1:end+1]
    timestamp_test = timestamps_Y[start+1:end+1]
    X_test = []
    X_test.append(XC_test)
    X_test.append(XP_test)
    X_test.append(XT_test)
    meta_feature_test = meta_feature[start+1:end+1]
    X_test.append(meta_feature_test)
    return X_test, Y_test, timestamp_test