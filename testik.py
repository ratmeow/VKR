import h5py
import datetime

def decode_time_steps(time_steps):
    new_time_steps = []
    for step in time_steps:
        new_time_steps.append(step.decode('utf-8'))
    return new_time_steps


def load_data():
    filename = 'R:/vkr2/fastapi\dao\BJ13_M32x32_T30_InOut.h5'
    with h5py.File(filename, 'r') as file:
        dataset_name = 'data'
        time_steps_name = 'date'
        dataset = file[dataset_name][:]
        time_steps = file[time_steps_name][:]
        return dataset, decode_time_steps(time_steps)


def get_one_shot(datetime: str):
    data, time_steps = load_data()
    idx = 0
    if datetime.encode('utf-8') in time_steps:
        for step in time_steps:
            if step.decode('utf-8') == datetime:
                break
            idx += 1
    else:
        return "No data"
    one_data = data[idx]

    inflow = one_data[0]
    outflow = one_data[1]

    return inflow, outflow


def check_miss_data():
    dataset, time_steps = load_data()
    start = time_steps[0][:8]
    end = time_steps[len(time_steps)-1][:8]
    start_date = datetime.datetime.strptime(start, "%Y%m%d")
    end_date = datetime.datetime.strptime(end, "%Y%m%d")
    missing_dates = []
    partial_dates = []
    complete_dates = []

    for d in range((end_date - start_date).days + 1):
        date = start_date + datetime.timedelta(days=d)
        date_str = date.strftime("%Y%m%d")
        date_steps = [step for step in time_steps if step.startswith(date_str)]
        if not date_steps:
            missing_dates.append(date_str)
        elif len(date_steps) < 48:
            partial_dates.append(date_str)
        else:
            complete_dates.append(date.strftime("%Y-%m-%d"))

    return complete_dates


def load_weather():
    filename = 'R:/vkr2/fastapi\dao\BJ_Meteorology.h5'
    with h5py.File(filename, 'r') as file:
        temp = file['Temperature'][:]
        weather = file['Weather'][:]
        wind = file['WindSpeed'][:]
        time_steps = decode_time_steps(file['date'][:])

        all_weather = {
            'date': time_steps,
            'temperature': temp,
            'wind': wind,
            'weather': weather
        }
        return all_weather


def convert_weather_type(weather_array):
    weather_types = {0: 'Sunny',
                     1: 'Cloudy',
                     2: 'Overcast',
                     3: 'Rainy',
                     4: 'Sprinkle',
                     5: 'ModerateRain',
                     6: 'HeavyRain',
                     7: 'Rainstorm',
                     8: 'Thunderstorm',
                     9: 'FreezingRain',
                     10: 'Snowy',
                     11: 'LightSnow',
                     12: 'ModerateSnow',
                     13: 'HeavySnow',
                     14: 'Foggy',
                     15: 'Sandstorm',
                     16: 'Dusty'}
    w = 1
    if w in weather_array:
        return weather_types[list(weather_array).index(w)]


def get_weather(datetime: str):
    weather = load_weather()
    time_steps = weather['date']
    idx = 0
    if datetime in time_steps:
        for step in time_steps:
            if step == datetime:
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

def load_events():
    filename = 'R:/vkr2/fastapi\dao\BJ_Holiday.txt'
    events = []
    with open(filename, 'r') as file:
        for event in file:
            events.append(event.strip())
    return events

def get_events(datetime:str):
    events = load_events()
    if datetime[:8] in events:
        return True
    return False


