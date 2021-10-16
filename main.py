# Hands on FastAPI
# Afif Fahreza / 18219058

import json
from fastapi import FastAPI, HTTPException

with open("menu.json", "r") as read_file:
    data = json.load(read_file)

app = FastAPI()

# READ ALL MENU
@app.get('/menu')
async def read_all_menu():
    if data['menu']:
        return data['menu']
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

# READ MENU BY ID
@app.get('/menu/{item_id}')
async def read_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(
        status_code=404, detail=f'Item not found'
    )

# CREATE MENU
@app.post('/menu')
async def create_menu(name: str):
    id = 1
    if len(data['menu'])>0:
        id += data['menu'][len(data['menu'])-1]['id']
    res = {'id': id, 'name': name}
    data['menu'].append(dict(res))
    if res:
        updateJson(data)
        return res
    raise HTTPException(
        status_code=400, detail=f'Bad request'
    )

# DELETE MENU
@app.delete('/menu/{item_id}')
async def delete_meu(item_id: int):
    for data_menu in data['menu']:
        if data_menu['id'] == item_id:
            data['menu'].remove(data_menu)
            updateJson(data)
            return data['menu']
    raise HTTPException(
        status_code=400, detail=f'Bad request'
    )

# UPDATE MENU
@app.put('/menu/{item_id}')
async def update_menu(item_id: int, name: str):
    for data_menu in data['menu']:
        if data_menu['id'] == item_id:
            data_menu["name"] = name
            updateJson(data)
            return data['menu']
    raise HTTPException(
        status_code=400, detail=f'Bad request'
    )

def updateJson(data):
    json_obj = json.dumps(data, indent=4)
    with open("menu.json", "w") as write_file:
        write_file.write(json_obj)