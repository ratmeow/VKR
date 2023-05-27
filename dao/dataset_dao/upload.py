import h5py


def decode_time_steps(time_steps):
    new_time_steps = []
    for step in time_steps:
        new_time_steps.append(step.decode('utf-8'))
    return new_time_steps


def load_data():
    filename = 'dao/TaxiBJ/BJ16_M32x32_T30_InOut.h5'
    with h5py.File(filename, 'r') as file:
        dataset_name = 'data'
        time_steps_name = 'date'
        dataset = file[dataset_name][:]
        time_steps = file[time_steps_name][:]
        return dataset, decode_time_steps(time_steps)


def load_weather():
    filename = 'dao/TaxiBJ/BJ_Meteorology.h5'
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


def load_events():
    filename = 'dao/TaxiBJ/BJ_Holiday.txt'
    events = []
    with open(filename, 'r') as file:
        for event in file:
            events.append(event.strip())
    return events


def convert_weather_type(weather_array):
    weather_types = {0: 'Солнечно',
                     1: 'Облачно',
                     2: 'Пасмурно',
                     3: 'Дождливо',
                     4: 'Мелкий дождь',
                     5: 'Умеренный дождь',
                     6: 'Сильный дождь',
                     7: 'Ливень',
                     8: 'Гроза',
                     9: 'Град',
                     10: 'Снежно',
                     11: 'Легкий снег',
                     12: 'Умеренный снег',
                     13: 'Сильный снег',
                     14: 'Туман',
                     15: 'Gесчаная буря',
                     16: 'Пыльно'}
    w = 1
    if w in weather_array:
        return weather_types[list(weather_array).index(w)]
