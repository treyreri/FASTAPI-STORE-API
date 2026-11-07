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

#create
@app.post("/categories/")
def create_category(payload: CategoryCreate):
    global category_id

    category_list[category_id] = { "title" : payload.title }
    created_category = { "id" : category_id , "title" : payload.title }
    category_id += 1
    return created_category

#read all categories
@app.get("/categories/")
def get_categories():
    return category_list

#read one category
@app.get("/categories/{category_id}")
def get_category(category_id: id):
    category = category_list.get(category_id)
    if category is None:
        raise HTTPException( status_code=404, detail="category not found" )
    return { "id" : category_id, **category }

#update category
@app.put("/categories/{category_id}")
def update_category( category_id: int, payload: CategoryUpdate ) :
    category = category_list.get(category_id)
    if category is None:
        raise HTTPException( status_code=404, detail="category not found" )
    category["title"] = payload.title
    return { "id" : category_id, **category }


#delete category
@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    category = category_list.get(category_id)
    if category is None:
        raise HTTPException( status_code=404, detail = "category not found" )
    for product in product_list.values():
        if product["category_id"] == category_id:
            raise HTTPException( status_code=400, detail = "category contains products" )

    del category_list[category_id]
    return { "message" : "category deleted successfully" }

#нельзя удалить категорию, если в ней уже находятся товары
# Иначе у товара останется ссылка на несуществующую категорию


# PRODUCT CRUD
product_list = {}
product_id = 1  

# PYDANTIC - MODELS
class ProductCreate(BaseModel):
    title : str = Field(min_length=2)
    category_id : int

class ProductUpdate(BaseModel):
    title : str | None = Field(default=None, min_length= 2)
    category_id : int | None = None

#CREATE PRODUCT
@app.post("/products/")
def create_product(payload: ProductCreate):
    global product_id
    category = category_list.get(payload.category_id) #важная проверка по айди
    if category is None:
        raise HTTPException( status_code=404, detail="category not found" )
    product_list[product_id] = { "title" : payload.title, "category_id" : payload.category_id }
    created_product = { "id" : product_id, **product_list[product_id] }
    product_id += 1
    return created_product

#read all products
@app.get("/products/")
def get_products():
    return product_list

#read one  product
@app.get("/products/{product_id}")
def get_product( product_id: int ) :
    product = product_list.get(product_id)
    if product is None:
        raise HTTPException( status_code=404, detail = "product not found" )
    return { "id" : product_id, **product }

#UPDATE PRODUCT
@app.patch("/products/{product_id}")
def update_product( product_id : int, payload: ProductUpdate ):
    product = product_list.get(product_id)
    if product is None:
        raise HTTPException( status_code= 404, detail = "product not found" )
    changes = payload.model_dump( exclude_unset = True, exclude_none= True ) # получаем только те поля, которые пользователь действительно передал

    if "category_id" in changes:
        category = category_list.get(changes["category_id"])
        if category is None:
            raise HTTPException( status_code=404, detail="category not found" )

    if not changes:
        raise HTTPException( status_code=400, detail = "No data provided" )
    product.update(changes)
    return { "id" : product_id, **product }

#delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = product_list.get(product_id)
    if product is None:
        raise HTTPException( status_code=404, detail = "product not found" )
    for item in orderitem_list.values():
        if item["product_id"] == product_id:
            raise HTTPException( status_code=400, detail = "product is used in an order" )
    del product_list[product_id]
    return {"message" : "product deleted successfully"}
# мы проверяем, не используется ли товар в существующем заказе




# ORDER создание и управление заказами . Заказ принадлежит пользователю который сейчас авторизован
order_list = {}
order_id = 1

#create order
@app.post("/orders/")
def create_order():
    global order_id
    if user_login is None:
        raise HTTPException( status_code=401, detail="please login first" )
    order_list[order_id] = {"user_id" : user_login}
    created_order = { "id" : order_id, **order_list[order_id] }
    order_id += 1
    return created_order
# user_login -> "user_id" : 1


# read all orders
@app.get("/orders/")
def get_orders():
    if user_login is None:
        raise HTTPException( status_code=401, detail="please login first" )
    result = {}

    for id, order in order_list.items():
        if order["user_id"] == user_login:
            result[id] == order
    return result
# ЗДЕСЬ МЫ ПОКАЗЫВАЕМ ТОЛЬКО ЗАКАЗЫ ТЕКУЩЕГО ПОЛЬЗОВАТЕЛЯ


# read one order
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    if user_login is None:
        raise HTTPException( status_code=401, detail=" please login first" )
    order = order_list.get(order_id)

    if order is None:
        raise HTTPException( status_code=404, detail="order not found" )

    if order["user_id"] != user_login:
        raise HTTPException( status_code=403, detail="this order belongs to another user" )
    return { "id": order_id, **order }


#delete order
@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    if user_login is None:
        raise HTTPException( status_code=401, detail = "please login first" )
    order = order_list.get(order_id)
    if order is None:
        raise HTTPException( status_code=404, detail="Order not found" )
    if order["user_id"] != user_login:
        raise HTTPException( status_code=403, detail = "you cannot delete rhis order" )
    items_to_delete = []
    for id, item in orderitem_list.items():
        if item["order_id"] == order.id:
            items_to_delete.append(id)

    for id in items_to_delete:
        del orderitem_list[id]

    del order_list[order_id]
    return { "message" : "order deleted successfully" }
#сначала находим все orderitems, которые принадлежат удаляемому заказу, потом удаляем их.
#И только после этого удаляем сам заказ. Так мы не оставляем ордерайтемс которые ссылаются на уже удаленный заказ