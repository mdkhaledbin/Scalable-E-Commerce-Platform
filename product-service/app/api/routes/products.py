from app.db import get_db
from app.models import Product
from app.schemas import ProductBase, ProductRead, ProductUpdate

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated


# Dependency alias to inject a scoped SQLAlchemy session per request.
DB_Session = Annotated[Session, Depends(get_db)]

router = APIRouter(tags=["Products"], prefix="/products")

@router.get("/all", summary="Get all products", status_code=200, response_model=list[ProductRead])
def get_all_products(db:DB_Session) -> list[ProductRead]:
    """Return the complete product catalog ordered by identifier."""
    products = db.execute(select(Product).order_by(Product.id))
    return list(products.scalars().all())

@router.get("/{id}", summary="Get Products with Id", status_code=200, response_model=ProductRead)
def get_products_with_id(id:int, db:DB_Session) -> ProductRead:
    """Fetch a single product or raise 404 when it does not exist."""
    product = db.execute(select(Product).where(Product.id == id)).scalar_one_or_none()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not present.")
    
    return product

@router.post("/create", summary="create a product", status_code=201, response_model=ProductRead)
def create_product(req_product:ProductBase, db:DB_Session) -> ProductRead:
    """Insert a new product ensuring name uniqueness."""
    product = db.execute(select(Product).where(Product.name==req_product.name)).scalar_one_or_none()
    
    if product is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists.")
    try:
        product = Product(
            name = req_product.name,
            price = req_product.price,
            description = req_product.description,
            category = req_product.category,
            stock = req_product.stock
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Product creation failed.")


@router.put("/update/{id}", summary="Update a product", status_code=200, response_model=ProductRead)
def update_product(id: int, req_product: ProductUpdate, db: DB_Session) -> ProductRead:
    """Apply partial updates to a product, mutating only provided fields."""
    product = db.execute(select(Product).where(Product.id == id)).scalar_one_or_none()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product is not present")
    
    try:
        if req_product.name is not None:
            product.name = req_product.name
        if req_product.price is not None:
            product.price = req_product.price
        if req_product.description is not None:
            product.description = req_product.description
        if req_product.category is not None:
            product.category = req_product.category
        if req_product.stock is not None:
            product.stock = req_product.stock
            
        db.commit()
        db.refresh(product)
        
        return product
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Product creation failed.")
    
@router.delete("/{id}", summary="Delete a product", status_code=200, response_model=ProductRead)
def delete_product(id:int,db:DB_Session)->ProductRead:
    """Remove a product from the catalog and return the deleted record."""
    product = db.execute(select(Product).where(Product.id == id)).scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exists.") 
    db.delete(product)
    db.commit()
    return product