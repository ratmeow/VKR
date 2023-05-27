import datetime
import math
from datetime import datetime, timedelta

import numpy as np

from .upload import load_data, load_weather, load_events, convert_weather_type
from model.eval import evaluate
from dao.dataset_dao.upload import decode_time_steps
from model.dataset import TaxiBJDataset


def get_city_state_at_time(datetime: str):
    data, time_steps = load_data()
    idx = 0
    if datetime in time_steps:
        for step in time_steps:
            if step == datetime:
                break
            idx += 1
    else:
        return "No data"
    one_data = data[idx]

    inflow = one_data[0]
    outflow = one_data[1]

    return inflow, outflow


def get_some_shots_for_cell(datetime_str: str, number: int, depth: int):
    data, time_steps = load_data()
    date_str = datetime_str[:8]

    col = math.floor(number / 32)
    row = number % 32

    date = datetime.strptime(date_str, '%Y%m%d')
    inflow_list = []
    outflow_list = []
    for day in range(depth, -1, -1):
        current_date = date - timedelta(days=day)
        current_date_str = current_date.strftime('%Y%m%d')
        start = current_date_str + '01'
        end = current_date_str + '48'
        if (start in time_steps) and (end in time_steps) and (time_steps.index(end) - time_steps.index(start) == 47):
            start_index = time_steps.index(start)
            end_index = time_steps.index(end)
            inflow_data = []
            outflow_data = []

            for i in range(start_index, end_index + 1):
                inflow_data.append(data[i][0][row][col])
                outflow_data.append(data[i][1][row][col])

            inflow_dict = {'date': f'{current_date_str}', 'data': inflow_data}
            outflow_dict = {'date': f'{current_date_str}', 'data': outflow_data}
            inflow_list.append(inflow_dict)
            outflow_list.append(outflow_dict)
        else:
            inflow_list.append({'date': f'{current_date_str}', 'data': []})
            outflow_list.append({'date': f'{current_date_str}', 'data': []})

    return inflow_list, outflow_list


def get_complete_days_from_data():
    dataset, time_steps = load_data()
    start = time_steps[0][:8]
    end = time_steps[len(time_steps)-1][:8]
    start_date = datetime.strptime(start, "%Y%m%d")
    end_date = datetime.strptime(end, "%Y%m%d")
    missing_dates = []
    partial_dates = []
    complete_dates = []

    for d in range((end_date - start_date).days + 1):
        date = start_date + timedelta(days=d)
        date_str = date.strftime("%Y%m%d")
        date_steps = [step for step in time_steps if step.startswith(date_str)]
        if not date_steps:
            missing_dates.append(date_str)
        elif len(date_steps) < 48:
            partial_dates.append(date_str)
        else:
            complete_dates.append(date.strftime("%Y-%m-%d"))

    return complete_dates


def get_weather(date_time: str):
    weather = load_weather()
    time_steps = weather['date']
    idx = 0
    if date_time in time_steps:
        for step in time_steps:
            if step == date_time:
                break
            idx += 1
    else:
        return "No data"

    this_weather = {
        'temperature': weather['temperature'][idx],
        'wind': weather['wind'][idx],
        'weather': convert_weather_type(weather['weather'][idx])
    }

    return this_weather


def get_events(date_time:str):
    events = load_events()
    if date_time[:8] in events:
        return True
    return False


def get_predict(dataset: TaxiBJDataset, date_time: str):
    dataset_timestamps = decode_time_steps(dataset.timestamps_Y)
    start = dataset_timestamps.index('2016032711')
    end = dataset_timestamps.index(date_time)
    evaluate_predict, rmse = evaluate(dataset, start, end)
    predict = (evaluate_predict[0]).detach().numpy()
    inflow, outflow = predict[0], predict[1]
    return {'inflow': inflow, 'outflow': outflow, 'rmse': rmse}


def get_predict_for_cell(datetime_str: str, number: int, dataset: TaxiBJDataset):
    dataset_timestamps = decode_time_steps(dataset.timestamps_Y)
    start = dataset_timestamps.index('2016032711')
    end = dataset_timestamps.index(datetime_str)
    predicts = (evaluate(dataset, start, end, cell_mode=True))

    col = math.floor(number / 32)
    row = number % 32

    start_time = 11
    steps_count = len(predicts)

    inflow_list = []
    outflow_list = []

    if start_time + steps_count > 48:
        new_day_steps = (steps_count + start_time) % 48

        need_predicts = predicts[-new_day_steps:]

        for predict_time_step in need_predicts:
            predict = predict_time_step[0].detach().numpy()
            inflow, outflow = predict[0], predict[1]
            inflow_list.append(int(inflow[row][col]))
            outflow_list.append(int(outflow[row][col]))

    else:
        for predict_time_step in predicts:
            predict = predict_time_step[0].detach().numpy()
            inflow, outflow = predict[0], predict[1]
            inflow_list.append(int(inflow[row][col]))
            outflow_list.append(int(outflow[row][col]))

    return inflow_list, outflow_list
