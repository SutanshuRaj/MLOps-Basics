### Reference: https://bit.ly/3Y9Yn7k

import os
import json
from fastapi import FastAPI, Path, Query, Body, Depends, HTTPException
from models import Employee, Admin
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from jose import jwt
from bson import json_util
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

app = FastAPI()
connect(db='hr_manage', host='localhost', port=27017)


class newUser(BaseModel):
    name: str
    age: int = Body(..., gt=21)
    teams: list
    emp_id: int


class newAdmin(BaseModel):
    username: str
    password: str


@app.get("/")
async def home():
    return {'message': 'Hello from MongoDB.'}


@app.get("/users/")
async def get_all_users():
    users = Employee.objects().to_json()
    users = json.loads(users)
    return {"users": users}


@app.get("/users/{user_id}")
async def get_specific_user(user_id: int = Path(..., gt=0)):
    user = Employee.objects.get(emp_id=user_id)
    user_dict = json.loads(user.to_json())
    return user_dict


@app.get("/users")
async def search_specific_user(name: str, age: int = Query(None, gt=18)):
    user = Employee.objects.filter(Q(name__icontains=name) | Q(age=age))
    user_dict = json.loads(user.to_json())
    return user_dict


@app.post("/add/")
async def add_new_user(item: newUser):
    new_user = Employee(name=item.name,
                        age=item.age,
                        teams=item.teams,
                        emp_id=item.emp_id)

    new_user.save()
    return {"message": "User added Successfully."}


# Hashing
pwd_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_pwd_hash(pwd):
    return pwd_hash.hash(pwd)


@app.post("/sign_up/")
def sign_up(item: newAdmin):
    new_admin = Admin(username=item.username,
                      password=get_pwd_hash(item.password))

    new_admin.save()
    return {"message": "New Admin Sign-up."}


# JWT
oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = 'HS256'


def auth_user(username, password):
    try:
        uname = json.loads(Admin.objects.get(username=username).to_json())
        pwd = pwd_hash.verify(password, uname["password"])
        return pwd
    except Admin.DoesNotExist:
        return False


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    to_expire = json.dumps(datetime.utcnow() + expires_delta, default=json_util.default)
    to_encode.update({"expires": to_expire})

    to_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return to_jwt


@app.post("/token/")
async def gen_token(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    if auth_user(username, password):
        access_token = create_access_token(
            data={"sub": username}, expires_delta=timedelta(minutes=60))
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect Username / Password.")


@app.get("/login/")
async def check_login(token: str = Depends(oauth2_schema)):
    return {'token': token}
