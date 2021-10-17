# UTS II3160 Teknologi Sistem Terintegrasi - API
# Afif Fahreza / 18219058

# Import Libraries
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# Read Json File
with open("menu.json", "r") as read_file:
    data = json.load(read_file)

# API
app = FastAPI()


class ItemCreate(BaseModel):  # Create data transfer object (ID auto increment)
    name: str


class ItemUpdate(BaseModel):  # Update data transfer object
    id: int
    name: str


@app.get('/menu')  # READ ALL MENU
async def read_all_menu():
    if data['menu']:
        return data['menu']
    raise HTTPException(status_code=404, detail=f'Item not found')


@app.get('/menu/{item_id}')  # READ MENY BY ID
async def read_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(status_code=404, detail=f'Item not found')


@app.post('/menu')  # CREATE MENU
async def create_menu(item: ItemCreate):
    id = 1
    if len(data['menu']) > 0:
        id += data['menu'][len(data['menu'])-1]['id']
    item_dict = item.dict()
    res = {'id': id, 'name': item_dict['name']}
    data['menu'].append(dict(res))
    if res:
        with open("menu.json", "w") as write_file:
            json.dump(data, write_file)
        write_file.close()
        return res
    raise HTTPException(status_code=400, detail=f'Bad request')


@app.delete('/menu/{item_id}')  # DELETE MENU BY ID
async def delete_meu(item_id: int):
    item_found = False
    for data_idx, data_menu in enumerate(data['menu']):
        if data_menu['id'] == item_id:
            tmp = data_menu
            item_found = True
            data['menu'].pop(data_idx)
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file)
            write_file.close()
            return tmp
    if not item_found:
        return "Menu ID not found"
    raise HTTPException(status_code=400, detail=f'Item not found')


@app.put('/menu/{item_id}')  # UPDATE MENU BY ID
async def update_menu(item_id: int, item: ItemUpdate):
    item_dict = item.dict()
    item_found = False
    for data_idx, item_data in enumerate(data['menu']):
        if item_data['id'] == item_id:
            item_found = True
            data['menu'][data_idx] = item_dict
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file)
            write_file.close()
            return item_data
    if not item_found:
        return "Menu ID not found"
    raise HTTPException(status_code=400, detail=f'Item not found')
