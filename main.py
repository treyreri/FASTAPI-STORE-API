from fastapi import FastAPI, HTTPException 
app = FastAPI( title = "shop API" , description="online shop backend" )

@app.get("/")
def home():
    return{ "message" : "welcome to shop api" }

user_list = {}
user_id = 1
user_login = None


class userCreate(BaseModel):
    username: str
    password: str

@app.post("/users/")
def create_user(payload: userCreate):
    global user_id #позволяет изменять переменную user_id, которая находится вне функции
    for user in user_list.values(): # valuse возращает значения словаря
        if user["username"] == payload.username:
            raise HTTPException( status_code= 400, detail = "username already exists" )
    
    user_list[user_id] = { "username" : payload.username, "password" : payload.password } #добавляем пользователя в словарь
    
    created_user = {
        "id" : user_id,
        "username" : payload.username }

    user_id += 1 # увеличиваем id для следующего пользователя
    return created_user

# USERLOGIN
class UserLogin( BaseModel ):
    username : str
    password : str

@app.post("/login/")
def login(payload: UserLogin):
    global user_login
    for id, user in user_list.items(): # .items возвращает пары tuple (1, {"username"...})
        if ( user["username"] == payload.username and user["password"] == payload.password ):
            user_login = id
            return {
                "message" : "successfully logged in" , 
                "user_id" : user_login
            }
    raise HTTPException(status_code=401, detail="invalid username or password")


@app.post("/logout/")
def logout():
    global user_login
    if user_login is None:
        raise HTTPException( status_code=401, detail="you are not logged in" )
    user_login = None
    return { "message" : "successfully logged out" }







from pydantic import BaseModel, Field
#CATEGORY CRUD
category_list = {}
category_id = 1

class CategoryCreate(BaseModel):
    title : str = Field(min_length=2)

class CategoryUpdate(BaseModel):
    title : str = Field(min_length=2)

@app.post("/categories/")
def create_category(payload: CategoryCreate):
    global category_id

    category_list[category_id] = { "title" : payload.title }
    created_category = { "id" : category_id , "title" : payload.title }
    category_id += 1
    return created_category