from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from dao.dataset_dao.getData import get_city, get_cell_info
from dao.dataset_dao.utils import get_complete_days_from_data, get_avaliable_models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/city/dates")
def get_available_dates():
    return get_complete_days_from_data()

@app.get("/city/models")
def get_available_models():
    return get_avaliable_models()

@app.get("/city/inflows/{date}/{time}/predict")
def get_inflows_predict(date: str, time: str):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    city_info = get_city(datetime, True)
    if city_info:
        city_info['state'] = city_info['state'][0]
        city_info['predict'] = city_info['predict'][0]
        return city_info
    else:
        return {"error": "Невозможно сделать прогноз на данную дату(недостаток данных), пожалуйста выберите другую дату"}


@app.get("/city/outflows/{date}/{time}/predict")
def get_outflows_predict(date: str, time: str):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    city_info = get_city(datetime, True)
    if city_info:
        city_info['state'] = city_info['state'][1]
        city_info['predict'] = city_info['predict'][1]
        return city_info
    else:
        return {"error": "Невозможно сделать прогноз на данную дату(недостаток данных), пожалуйста выберите другую дату"}


@app.get("/city/inflows/{date}/{time}")
def get_inflows(date: str, time: str):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    city_info = get_city(datetime)
    city_info['state'] = city_info['state'][0]
    return city_info


@app.get("/city/outflows/{date}/{time}")
def get_outflows(date: str, time: str):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    city_info = get_city(datetime)
    city_info['state'] = city_info['state'][1]
    return city_info


@app.get("/cell/inflows/{cell_id}/{date}/{time}")
def get_cell_inflow(date: str, time: str, cell_id: int):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    inflows, _ = get_cell_info(datetime, cell_id, depth=1)
    return inflows


@app.get("/cell/outflows/{cell_id}/{date}/{time}")
def get_cell_outflow(date: str, time: str, cell_id: int):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    _, outflows = get_cell_info(datetime, cell_id, depth=1)
    return outflows


@app.get("/cell/inflows/{cell_id}/{date}/{time}/predict")
def get_cell_inflow_predict(date: str, time: str, cell_id: int):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    predict_inflows, _ = get_cell_info(datetime, cell_id, predict_mode=True)
    true_inflows, _ = get_cell_info(datetime, cell_id, depth=1)
    return {'true_data': true_inflows, 'predict_data': predict_inflows}


@app.get("/cell/outflows/{cell_id}/{date}/{time}/predict")
def get_cell_outflow_predict(date: str, time: str, cell_id: int):
    new_date = ''.join(date.split('-'))
    datetime = new_date + time
    _, predict_outflows = get_cell_info(datetime, cell_id, predict_mode=True)
    _, true_outflows = get_cell_info(datetime, cell_id, depth=1)
    return {'true_data': true_outflows, 'predict_data': predict_outflows}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)