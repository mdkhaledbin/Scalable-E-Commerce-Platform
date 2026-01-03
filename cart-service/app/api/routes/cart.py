from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Cart, CartItem
from app.schemas import (
    CartItemCreate,
    CartItemReplace,
    CartItemUpdate,
    CartCreate,
    CartRead,
    CartUpdate,
)

from typing import Annotated


DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/carts", tags=["carts"])


def _cart_query(user_id: int | None = None, cart_id: int | None = None):
    stmt = select(Cart).options(selectinload(Cart.items))
    if user_id is not None:
        stmt = stmt.where(Cart.user_id == user_id)
    if cart_id is not None:
        stmt = stmt.where(Cart.id == cart_id)
    return stmt


def _get_cart_or_404(db: Session, user_id: int) -> Cart:
    cart = db.execute(_cart_query(user_id=user_id)).scalar_one_or_none()
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    return cart


def _reload_cart(db: Session, cart_id: int) -> Cart:
    return db.execute(_cart_query(cart_id=cart_id)).scalar_one()


def _materialize_item(payload: CartItemCreate) -> CartItem:
    return CartItem(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
    )


@router.get("/{user_id}", summary="Get the user's cart", response_model=CartRead,status_code=status.HTTP_200_OK)
def get_cart(user_id: int, db: DbSession) -> CartRead:
    return _get_cart_or_404(db, user_id)


@router.post("", summary="Create a cart", response_model=CartRead, status_code=status.HTTP_201_CREATED)
def create_cart(payload: CartCreate, db: DbSession) -> CartRead:
    existing = db.execute(_cart_query(user_id=payload.user_id)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart already exists")

    cart = Cart(user_id=payload.user_id, status=payload.status)
    for item in payload.items:
        cart.items.append(_materialize_item(item))

    db.add(cart)
    db.commit()
    return _reload_cart(db, cart.id)


@router.post("/{user_id}/items", summary="Add or increment an item", response_model=CartRead)
def add_item(user_id: int, item: CartItemCreate, db: DbSession) -> CartRead:
    cart = db.execute(_cart_query(user_id=user_id)).scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()

    existing_item = next((ci for ci in cart.items if ci.product_id == item.product_id), None)
    if existing_item is not None:
        existing_item.quantity += item.quantity
        existing_item.unit_price = item.unit_price
    else:
        cart.items.append(_materialize_item(item))

    db.commit()
    return _reload_cart(db, cart.id)


@router.patch("/status/{user_id}", summary="Update cart status", response_model=CartRead)
def update_cart(user_id: int, payload: CartUpdate, db: DbSession) -> CartRead:
    if payload.status is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")

    cart = _get_cart_or_404(db, user_id)
    if payload.status is not None:
        cart.status = payload.status

    db.commit()
    return _reload_cart(db, cart.id)


@router.patch(
    "/{user_id}/items/{product_id}",
    summary="Update item quantity or price",
    response_model=CartRead,
)
def update_item(user_id: int, product_id: int, payload: CartItemUpdate, db: DbSession) -> CartRead:
    if payload.quantity is None and payload.unit_price is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")

    cart = _get_cart_or_404(db, user_id)
    item = next((ci for ci in cart.items if ci.product_id == product_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.unit_price is not None:
        item.unit_price = payload.unit_price

    db.commit()
    return _reload_cart(db, cart.id)


@router.put("/{user_id}/items", summary="Replace all items", response_model=CartRead)
def replace_items(user_id: int, payload: CartItemReplace, db: DbSession) -> CartRead:
    cart = _get_cart_or_404(db, user_id)
    cart.items.clear()
    for item in payload.items:
        cart.items.append(_materialize_item(item))

    db.commit()
    return _reload_cart(db, cart.id)


@router.delete(
    "/{user_id}/items/{product_id}",
    summary="Remove a single item",
    response_model=CartRead,
)
def remove_item(user_id: int, product_id: int, db: DbSession) -> CartRead:
    cart = _get_cart_or_404(db, user_id)
    item = next((ci for ci in cart.items if ci.product_id == product_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()
    return _reload_cart(db, cart.id)


@router.delete("/{user_id}/items", summary="Remove all items", response_model=CartRead)
def clear_cart(user_id: int, db: DbSession) -> CartRead:
    cart = _get_cart_or_404(db, user_id)
    cart.items.clear()
    db.commit()
    return _reload_cart(db, cart.id)


@router.delete("/{user_id}", summary="Delete the cart", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(user_id: int, db: DbSession) -> None:
    cart = db.execute(_cart_query(user_id=user_id)).scalar_one_or_none()
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

    db.delete(cart)
    db.commit()
