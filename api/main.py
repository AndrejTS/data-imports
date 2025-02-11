from typing import Optional, Union, List

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, HttpUrl, RootModel
from celery import Celery
from celery.result import AsyncResult

app = FastAPI()

celery = Celery(
    "fast_api", broker="redis://redis:6379/0", backend="redis://redis:6379/1"
)

mongo_client = AsyncIOMotorClient("mongodb://mongodb:27017")
db = mongo_client["my_mongo_db"]


class User(BaseModel):
    username: str
    website_id: str


class EnhancedData(BaseModel):
    website_id: str

    class Config:
        extra = "allow"


class EnhancedProductResponse(RootModel[EnhancedData]):
    pass


class ProductResponse(BaseModel):
    product_id: Optional[str] = None
    website_id: Optional[str] = None
    product_url: Optional[HttpUrl] = None
    sku: Optional[str] = None
    name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    images_gallery: Optional[List[HttpUrl]] = None
    category: Optional[Union[str, List[str]]] = None
    availability: Optional[str] = None
    availability_extracted: Optional[str] = None
    brand_extracted: Optional[str] = None
    enhanced_data: Optional[EnhancedData] = None


class PaginatedEnhancedProductsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    enhanced_products: List[EnhancedProductResponse]


class PaginatedProductsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    products: List[ProductResponse]


class ImportRequest(BaseModel):
    website_id: str


fake_users_db = {
    "drone-user": User(username="drone-user", website_id="drone-fpv-racer.com"),
    "electro-user": User(username="electro-user", website_id="electronics-shop.com"),
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real case, decoding a JWT would be there
    user = fake_users_db.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simplified authentication
    user = fake_users_db.get(form_data.username)
    if not user or form_data.password != "pass":
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    return {"access_token": form_data.username, "token_type": "bearer"}


@app.post("/imports/start", status_code=status.HTTP_202_ACCEPTED)
async def start_import(
    import_request: ImportRequest, current_user: User = Depends(get_current_user)
):
    if current_user.website_id != import_request.website_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this website denied",
        )

    task = celery.send_task(
        "import_data",
        args=[import_request.website_id],
    )

    return {"task_id": task.id, "status": "Import started"}


@app.get("/imports/status/{task_id}")
async def get_import_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, current_user: User = Depends(get_current_user)):
    product = await db["products"].find_one({"product_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.pop("_id", None)

    if current_user.website_id == product.get("website_id"):
        enhanced = await db["enhanced_products"].find_one({"product_id": product_id})
        if enhanced:
            enhanced.pop("_id", None)
            product["enhanced_data"] = enhanced

    return product


@app.get("/products", response_model=PaginatedProductsResponse)
async def get_all_products(
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    skip = (page - 1) * page_size

    total = await db["products"].count_documents(
        {"website_id": current_user.website_id}
    )

    cursor = (
        db["products"]
        .find({"website_id": current_user.website_id})
        .skip(skip)
        .limit(page_size)
    )

    products = []
    async for product in cursor:
        product.pop("_id", None)

        if current_user.website_id == product.get("website_id"):
            enhanced = await db["enhanced_products"].find_one(
                {"product_id": product["product_id"]}
            )
            if enhanced:
                enhanced.pop("_id", None)
                product["enhanced_data"] = enhanced

        products.append(product)

    return {"total": total, "page": page, "page_size": page_size, "products": products}


@app.get("/enhanced-products/search", response_model=EnhancedProductResponse)
async def get_enhanced_product(
    search_field: str = Query(...),
    search_value: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    query = {"website_id": current_user.website_id, search_field: search_value}

    enhanced = await db["enhanced_products"].find_one(query)
    if not enhanced:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enhanced data for this product was not found.",
        )

    enhanced.pop("_id", None)

    return enhanced


@app.get("/enhanced-products", response_model=PaginatedEnhancedProductsResponse)
async def get_all_enhanced_products(
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    skip = (page - 1) * page_size

    total = await db["enhanced_products"].count_documents(
        {"website_id": current_user.website_id}
    )

    cursor = (
        db["enhanced_products"]
        .find({"website_id": current_user.website_id})
        .skip(skip)
        .limit(page_size)
    )

    enhanced_products = []
    async for enhanced in cursor:
        enhanced.pop("_id", None)
        enhanced_products.append(enhanced)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "enhanced_products": enhanced_products,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
