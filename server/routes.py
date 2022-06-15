#!/usr/bin/env python

import base64, os
from typing import Optional, Union, Callable
from json.decoder import JSONDecodeError
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from .schemas import ProductSchema, TransactionSchema, UserSchema
from .models import ConnectDB, ProductData, TransactionData, UserData

router: APIRouter
router = APIRouter()

connect_db: ConnectDB
connect_db = ConnectDB()

# print(dir(response))
## background body charset delete_cookie headers init_headers media_type raw_headers render set_cookie status_code

# print(dir(request))
## app auth base_url body client close cookies form get headers is_disconnected items json keys method path_params query_params receive scope send_push_promise session state stream url url_for user values

def route(*args, **kwargs):

    def wrapper(fn: Callable):

        if callable(fn):

            router.get(*args, **kwargs)(fn)
            router.post(*args, **kwargs)(fn)
            router.put(*args, **kwargs)(fn)
            router.delete(*args, **kwargs)(fn)
            router.patch(*args, **kwargs)(fn)

    return wrapper

def user_registry(body: dict, user_data: UserData) -> Optional[dict]:

    try:

        user: BaseModel
        user = UserSchema(**body)

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully registered user",
            "contents": [
                None
            ]
        }

        if not user_data.get_by_username(user.username):

            user_data.append(user)
            data: Optional[dict]
            data = user_data.get_by_username(user.username)
            result["contents"][0] = {
                "user_id": data["id"],
                "username": data["username"],
            }

        else:

            result["status_code"] = 400
            result["message"] = "User already registered"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def user_get(body: dict, user_data: UserData) -> Optional[dict]:

    try:

        username: Optional[str]
        password: Optional[str]
        username = None
        password = None

        if "username" in body:
            username = body["username"]

        if "password" in body:
            password = body["password"]

        if password is not None:
            password = base64.b64decode("".join(reversed(password))).decode("utf-8")

        data: Optional[dict]
        data = user_data.get_by_username(username)

        ## Hidden password
        ## Hidden Email
        ## Hidden Phone
        if password != data["password"]:
        
            data.update(email=None, phone=None)

        data.update(password=None)

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully get user",
            "contents": [
                data  
            ]
        }

        if not result.get("contents")[0]:

            result["status_code"] = 400
            result["message"] = "User not found!"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def product_registry(body: dict, product_data: ProductData) -> Optional[dict]:

    try:

        product: BaseModel
        product = ProductSchema(**body)

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully registered product"
        }

        if not product_data.get_by_name(product.name):

            product_data.append(product)

        else:

            result["status_code"] = 400
            result["message"] = "Product already registered"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def product_get(body: dict, product_data: ProductData) -> Optional[dict]:

    try:

        # product: BaseModel
        # product = ProductSchema(**body)

        id: int
        id = 0

        if "product_id" in body:
            id = body["product_id"]

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully get product",
            "contents": [
                product_data.get(id)
            ]
        }

        if not result.get("contents")[0]:

            result["status_code"] = 400
            result["message"] = "Product not found!"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def product_enrolls(body: dict, product_data: ProductData) -> Optional[dict]:

    try:

        # product: BaseModel
        # product = ProductSchema(**body)

        offset: int
        offset = 0

        limit: int
        limit = 20

        if "offset" in body:

            offset = body["offset"]

        if "limit" in body:

            limit = body["limit"]
        
        if "count" in body:

            limit = body["count"]

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully enrolled product",
            "contents": [ 
                product_data
                .splitter_categories(
                    # dict(
                    #     zip(
                    #         ProductSchema.__fields__.keys(), 
                    #         x
                    #     )
                    # )
                    x
                ) for x in product_data.get_all_products(
                    start_at=offset, 
                    count=limit
                ) 
            ]
        }

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def product_remove(body: dict, product_data: ProductData) -> Optional[dict]:

    try:

        # product: BaseModel
        # product = ProductSchema(**body)

        product_name: str
        product_name = body.get("name")

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully removed product"
        }

        product: Union[Optional[dict], ProductSchema]
        product = product_data.get_by_name(product_name)

        if product:

            product = ProductSchema(**product)

        if product:

            if (product_data.remove(product.id)):

                print("Successfully removed product!")

        else:

            result["status_code"] = 400
            result["message"] = "Product not found!"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def transaction_registry(body: dict, user_data: UserData, transaction_data: TransactionData) -> Optional[dict]:

    try:

        product_id: Optional[int]
        product_id = body.get("product_id")

        username: Optional[str]
        username = body.get("username")

        transaction: BaseModel
        transaction = TransactionSchema(**body)

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully registered transaction"
        }

        data: Optional[dict]
        data = user_data.get_by_username(username)

        user_id: int
        user_id = 0

        if "id" in data:
            
            user_id = data["id"]
        
        else:

            result["status_code"] = 400
            result["message"] = "User not found!"

        if user_id and product_id:

            transaction.user_id = user_id
            transaction.product_id = product_id
            
            if not transaction_data.append(transaction):

                pass

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def transaction_enrolls(body: dict, transaction_data: TransactionData) -> Optional[dict]:

    try:

        # transaction: TransactionSchema
        # transaction = TransactionSchema(**body)

        offset: int
        offset = 0

        limit: int
        limit = 20

        if "offset" in body:

            offset = body["offset"]

        if "limit" in body:

            limit = body["limit"]
        
        if "count" in body:

            limit = body["count"]

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully enrolled transaction",
            "contents": transaction_data.get_all_transactions(offset, limit)
        }

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

def transaction_remove(body: dict, transaction_data: TransactionData) -> Optional[dict]:

    try:

        # transaction: BaseModel
        # transaction = TransactionSchema(**body)

        transaction_id: int
        transaction_id = body.get("id")

        result: dict
        result = {

            "status_code": 200,
            "message": "Successfully removed product"
        }

        if transaction_id:

            if (transaction_data.remove(transaction_id)):

                print("Successfully removed transaction!")

        else:

            result["status_code"] = 400
            result["message"] = "Transaction not found!"

        connect_db.commit()

        return result

    except ValidationError as e:

        print(e.json())
                
    return None

@route("/v1/users/{name}")
async def users(name: str, request: Request, response: Response) -> Response: 

    # host: str
    # host = request.client.host

    # port: str
    # port = request.client.port

    body: Union[bytes, dict, None]
    body = await request.body()

    if body:
    
        try: 

            body = await request.json()
            
        except JSONDecodeError as e: 

            body = None

    else:

        body = None

    if isinstance(body, dict):

        user_data: UserData
        user_data = UserData(connect_db)
    
        if name in ("registry",):

            body = user_registry(body, user_data)

        elif name in ("get",):

            body = user_get(body, user_data)

        else:

            body = None

        if type(body) is dict:

            return JSONResponse(content=body)

    return JSONResponse(content={
        "status_code": 413,
        "message": "value missing!."
    })

@route("/v1/products/{name}")
async def products(name: str, request: Request, response: Response) -> Response: 

    # host: str
    # host = request.client.host

    # port: str
    # port = request.client.port

    body: Union[bytes, dict, None]
    body = await request.body()

    if body:
    
        try: 

            body = await request.json()
            
        except JSONDecodeError as e: 

            body = None

    else:

        body = None

    if isinstance(body, dict):

        product_data: ProductData
        product_data = ProductData(connect_db)
    
        if name in ("registry",):

            body = product_registry(body, product_data)

        elif name in ("enrolls",):

            body = product_enrolls(body, product_data)

        elif name in ("get",):

            body = product_get(body, product_data)

        elif name in ("remove",):

            body = product_remove(body, product_data)

        else:

            body = None

        if type(body) is dict:

            return JSONResponse(content=body)

    return JSONResponse(content={
        "status_code": 413,
        "message": "value missing!."
    })

@route("/v1/transactions/{name}")
async def transactions(name: str, request: Request, response: Response) -> Response: 

    # host: str
    # host = request.client.host

    # port: str
    # port = request.client.port

    body: Union[bytes, dict, None]
    body = await request.body()

    if body:
    
        try: 

            body = await request.json()
            
        except JSONDecodeError as e: 

            body = None

    else:

        body = None

    if isinstance(body, dict):

        user_data: UserData
        user_data = UserData(connect_db)

        transaction_data: TransactionData
        transaction_data = TransactionData(connect_db)
    
        if name in ("registry",):

            body = transaction_registry(body, user_data, transaction_data)

        elif name in ("enrolls",):

            body = transaction_enrolls(body, transaction_data)

        elif name in ("remove",):

            body = transaction_remove(body, transaction_data)

        else:

            body = None

        if type(body) is dict:

            return JSONResponse(content=body)

    return JSONResponse(content={
        "status_code": 413,
        "message": "value missing!."
    })

@route("/v1/test")
async def test(request: Request, response: Response) -> Response:

    db_exists: bool
    db_exists = os.path.exists(connect_db.src)

    #* db_writable: bool
    #* db_writable = open(connect_db.src, "wb").writable()

    return JSONResponse(content={
        "db_exists": db_exists
    })
