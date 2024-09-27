import json
from fastapi import FastAPI, Path, Query, Body, Depends
from models import Employee, Admin
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

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
    return {'message': 'Hello from MongoDB'}


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


# JWT and Hashing
pwd_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_pwd_hash(pwd):
    return pwd_hash.hash(pwd)


@app.post("/sign_up/")
def sign_up(item: newAdmin):
    new_admin = Admin(username=item.username,
                      password=get_pwd_hash(item.password))

    new_admin.save()
    return {"message": "New Admin Sign-up."}


oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token/")
async def gen_token():
    pass


@app.get("/login/")
async def check_login(token: str = Depends(oauth2_schema)):
    return {'message': 'Hello from MongoDB'}
