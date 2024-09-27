from fastapi import FastAPI
from enum import Enum
from pydantic import BaseModel

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

### Path Parameters.

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/blogs/{id}")
async def read_blog(id: int):
    return {"blog_id": id}

# @app.get("/blogs/{title}")
# async def read_blog(title):
#     return {"blog_title": title}

@app.get("/users/me")
async def read_user():
    return {'user_id': 'HEAD -> Current'}

@app.get("/users")
async def default_user():
    return ['John Doe']

@app.get("/models/{model_name}")
async def model_implemented(model_name: ModelName) -> dict:
    if model_name in ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == 'lenet':
        return {"model_name": model_name, "message": "LeCNN the Images."}
    return {"model_name": model_name, "message": "Have some Residuals."}


### Query Parameters.

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip : int = 0, limit : int = 10):
    return fake_items_db[skip : skip + limit]

### Equivalent: http://127.0.0.1:8000/items/?skip=0&limit=10

@app.get("/admin/{item_id}")
async def read_admin(item_id : str, uname : str | None = None):
    if uname:
        return {"item_id": item_id, "username": uname}
    return {"item_id": item_id}


### Request Body.

class CreateAdmin(BaseModel):
    name : str
    desc : str | None = None
    ver : int
    tag : list[str] | None = None


@app.post("/admin/")
async def create_admin(item: CreateAdmin) -> CreateAdmin:
    item_dict = item.dict()
    if item.desc:
        item_dict.update({'git' : 1})
    else:
        item_dict.update({'git' : 0})
    return item_dict


@app.put("/api/{item_id}")
async def update_endpoint(item_id: int, item: CreateAdmin, fname: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if fname:
        result.update({"function": fname})
    return result


@app.get("/api/")
async def read_endpoint() -> list[CreateAdmin]:
    return [
        CreateAdmin(name = 'Raj', ver = 1),
        CreateAdmin(name = 'Urmi', ver = 1, tag = ['SuperAdmin'])
    ]

