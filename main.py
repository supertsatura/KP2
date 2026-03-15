from fastapi import FastAPI, Cookie, Response, Path, Query, Form, HTTPException
from fastapi.params import Form
from pydantic import BaseModel, Field
from typing import Annotated
import uuid
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

# # 3.1
# app = FastAPI()
#
# class UserSchema(BaseModel):
#     name: Annotated[str, Field(...)]
#     email: Annotated[str, Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")]
#     age: Annotated[int, Field(ge=0)]
#     is_subscribed: Annotated[bool, Field(default=False)]
#
# @app.post("/user", response_model=UserSchema, status_code=201, tags=["User"], summary="Get user")
# async def create_user(user: UserSchema):
#     return user

# # 3.2
# app = FastAPI()
#
# sample_product_1 = {
#     "product_id": 123,
#     "name": "Smartphone",
#     "category": "Electronics",
#     "price": 599.99
# }
#
# sample_product_2 = {
#     "product_id": 456,
#     "name": "Phone Case",
#     "category": "Accessories",
#     "price": 19.99
# }
#
# sample_product_3 = {
#     "product_id": 789,
#     "name": "Iphone",
#     "category": "Electronics",
#     "price": 1299.99
# }
#
# sample_product_4 = {
#     "product_id": 101,
#     "name": "Headphones",
#     "category": "Accessories",
#     "price": 99.99
# }
#
# sample_product_5 = {
#     "product_id": 202,
#     "name": "Smartwatch",
#     "category": "Electronics",
#     "price": 299.99
# }
#
# sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]
#
#
# @app.get("/product/{product_id}", status_code = 200, tags=["Products"], summary="Get product by ID")
# async def get_product(product_id: Annotated[int, Path(...)]):
#     for product in sample_products:
#         if product["product_id"] == product_id:
#             return product
#     raise HTTPException(status_code=404, detail="Product not found")
#
#
# @app.get("/products/search", status_code = 200, tags=["Products"], summary="Search products by parameters")
# async def search_products(
#         keyword: Annotated[str, Query(...)],
#         category: Annotated[str, Query()] = None,
#         limit: Annotated[int, Query(ge=0)] = 10):
#     li = []
#
#     for product in sample_products[:limit]:
#         if (keyword.lower() in product["name"].lower()) or (
#                 keyword.lower() in product["name"].lower() and category.lower() in product["category"].lower()):
#             li.append(product)
#
#     if len(li) == 0:
#         raise HTTPException(status_code=404, detail="Product not found")
#
#     return li

# # 5.1
# app = FastAPI()
#
#
# class LoginRequestSchema(BaseModel):
#     username: str
#     password: str
#
#
# class UserProfileSchema(BaseModel):
#     id: int
#     username: str
#     full_name: str
#     email: str
#
#
# users = {
#     "Kudar": {
#         "id": 1,
#         "username": "Kudarets",
#         "password": "12345",
#         "email": "kudar@example.com",
#         "full_name": "Иван Иванов"
#     },
#     "Digoron": {
#         "id": 2,
#         "username": "Digorets",
#         "password": "54321",
#         "email": "alice@example.com",
#         "full_name": "Алиса Петрова"
#     }
# }
#
# active_sessions = {}
#
#
# @app.post("/login", status_code=201, tags=["User"], summary="User authentication")
# async def create_user(response: Response,
#                       username: Annotated[str, Form()],
#                       password: Annotated[str, Form()]):
#     user = users.get(username)
#     if not user or user["password"] != password:
#         raise HTTPException(status_code=401, detail="User not found")
#
#     session_token = str(uuid.uuid4())
#     active_sessions[session_token] = username
#     response.set_cookie(
#         key="session_token",
#         value=session_token,
#         httponly=True,
#         secure=True,
#         max_age=3600
#     )
#     return {"Message": "Login successful", "Username": username}
#
#
# @app.get("/user", status_code=200, response_model=UserProfileSchema, tags=["User"], summary="User info")
# async def get_user(session_token: Annotated[str | None, Cookie()] = None):
#     if not session_token or session_token not in active_sessions:
#         raise HTTPException(status_code=401, detail="Session token not found")
#     username = active_sessions[session_token]
#     user = users.get(username)
#     return user

# 5.2
app = FastAPI()
SECRET_KEY = "my-secret-key"
serializer = URLSafeTimedSerializer(SECRET_KEY)

users = {
    "David": {
        "user_id": str(uuid.uuid4()),
        "username": "Wfnehf",
        "password": "12345",
        "email": "wfnehf@example.com",
        "full_name": "David Ts"
    },
    "Ivan": {
        "user_id": str(uuid.uuid4()),
        "username": "ivan123",
        "password": "54321",
        "email": "ivanov@example.com",
        "full_name": "Ivan Ivanov"
    }
}

username_to_user = {user["username"]: user for user in users.values()}


class LoginRequestSchema(BaseModel):
    username: str
    password: str


class UserProfileSchema(BaseModel):
    user_id: str
    username: str
    full_name: str
    email: str


def verify_password(plain_password: str, stored_password: str) -> bool:
    # проверка пароля
    return plain_password == stored_password


def create_signed_session_token(user_id: str) -> str:
    # создание токена в формате <user_id>.<signature>
    signature = serializer.dumps(user_id)
    return f"{user_id}.{signature}"


@app.post("/login", status_code=201, tags=["User"], summary="User authentication")
async def create_user(response: Response, login_data: LoginRequestSchema):
    user = username_to_user.get(login_data.username)

    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password")

    session_token = create_signed_session_token(user["user_id"])

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        max_age=3600,
        samesite="lax"
    )

    return {
        "message": "Login successful",
        "username": login_data.username,
        "session_token": session_token
    }


@app.get("/profile", status_code=200, response_model=UserProfileSchema, tags=["User"], summary="User profiling")
async def get_profile(session_token: Annotated[str | None, Cookie()] = None):
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail={"message": "Unauthorized"}
        )
    try:
        user_id, signature = session_token.split(".", 1)
        verified_user_id = serializer.loads(signature, max_age=3600)
        if verified_user_id != user_id:
            raise HTTPException(
                status_code=401,
                detail={"message": "Unauthorized"}
            )
        user = next((u for u in users.values() if u["user_id"] == user_id), None)
        if not user:
            raise HTTPException(
                status_code=401,
                detail={"message": "Unauthorized"}
            )

        return user
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="User unauthorized")

