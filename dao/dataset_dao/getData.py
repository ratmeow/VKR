from .city import City
from .cell import Cell


def get_city(time: str, predict_mode=False):
    city_info = {}
    c = City(time, predict_mode)
    state = c.get_city_state()
    if predict_mode:
        predict_state = c.get_city_predict_state()
        city_info['predict'] = predict_state
        city_info['rmse'] = c.get_rmse()
    weather = c.get_city_weather()
    holiday = c.check_holiday()
    if holiday:
        holiday = 'Да'
    else:
        holiday = 'Нет'

    city_info['state'] = state
    city_info['weather'] = weather
    city_info['holiday'] = holiday
    return city_info


def get_cell_info(time: str, cell_id: int, predict_mode=False, depth=0):
    cell = Cell(cell_id, None, None)
    if predict_mode:
        return cell.get_predict_state(time)
    return cell.get_daily_state(time, depth)


