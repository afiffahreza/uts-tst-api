# UTS II3160 Teknologi Sistem Terintegrasi - API
# Afif Fahreza / 18219058

# Import Libraries
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import json

# secret key string from openssl rand -hex 32
SECRET_KEY = "02b55af9a51f87aea76b6406f5667f1341985add1c527afcbd2fcabb46318ab3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Read Json Files
with open("menu.json", "r") as read_file:
    data = json.load(read_file)
with open("users.json", "r") as read_file2:
    users = json.load(read_file2)


class Token(BaseModel):  # Token class
    access_token: str
    token_type: str


class TokenData(BaseModel):  # Token class
    username: Optional[str] = None


class User(BaseModel):  # User Auth
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):  # User Auth
    hashed_password: str


class UserCreate(BaseModel):  # User Auth
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class ItemCreate(BaseModel):  # Create data transfer class (ID auto increment)
    name: str


class ItemUpdate(BaseModel):  # Update data transfer class
    id: int
    name: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    for usernames in db['users']:
        if usernames["username"] == username:
            user_dict = usernames
            return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(
        users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=User)
async def register(user: UserCreate):
    newUser = user.dict()
    userJson = {
        'username': newUser['username'],
        'full_name': newUser['full_name'],
        'email': newUser['email'],
        'hashed_password': get_password_hash(newUser['password']),
        'disabled': False
    }
    users['users'].append(dict(userJson))
    if userJson:
        with open("users.json", "w") as write_file:
            json.dump(users, write_file)
        write_file.close()
        return userJson
    raise HTTPException(status_code=400, detail=f'Bad request')


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get('/menu')  # READ ALL MENU
async def read_all_menu(current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    if data['menu']:
        return data['menu']
    raise HTTPException(status_code=404, detail=f'Item not found')


@app.get('/menu/{item_id}')  # READ MENY BY ID
async def read_menu(item_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(status_code=404, detail=f'Item not found')


@app.post('/menu')  # CREATE MENU
async def create_menu(item: ItemCreate, current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
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
async def delete_menu(item_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
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
async def update_menu(item_id: int, item: ItemUpdate, current_user: User = Depends(get_current_active_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
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
