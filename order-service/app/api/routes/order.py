from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Order, OrderItem
from app.schemas import OrderCreate, OrderItemCreate, OrderItemUpdate, OrderRead, OrderUpdate

DB_Session = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_query(user_id: int | None = None, order_id: int | None = None):
    stmt = select(Order).options(selectinload(Order.items))

    if user_id is not None:
        stmt = stmt.where(Order.user_id == user_id)
    if order_id is not None:
        stmt = stmt.where(Order.id == order_id)

    return stmt.order_by(Order.created_at.desc())


def get_orders_or_404(user_id: int, db: Session) -> list[Order]:
    try:
        orders = db.execute(_order_query(user_id=user_id)).unique().scalars().all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders.",
        ) from exc

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No orders found for the user.",
        )

    return orders


def get_one_order_or_404(order_id: int, db: Session) -> Order:
    try:
        order = db.execute(_order_query(order_id=order_id)).unique().scalar_one_or_none()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order.",
        ) from exc

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")

    return order


def reload_orders(user_id: int, db: Session) -> list[Order]:
    return db.execute(_order_query(user_id=user_id)).unique().scalars().all()


def reload_one_order(order_id: int, db: Session) -> Order:
    return db.execute(_order_query(order_id=order_id)).unique().scalar_one()


def _materialize_item(payload: OrderItemCreate) -> OrderItem:
    return OrderItem(
        product_id=payload.product_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
    )


@router.get("", summary="List orders", response_model=list[OrderRead])
def list_orders(db: DB_Session) -> list[OrderRead]:
    try:
        result = db.execute(_order_query())
        return result.unique().scalars().all()
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders.",
        ) from exc


@router.get("/users/{user_id}", summary="List orders for a user", response_model=list[OrderRead])
def list_orders_for_user(user_id: int, db: DB_Session) -> list[OrderRead]:
    return get_orders_or_404(user_id, db)


@router.get("/{order_id}", summary="Retrieve an order", response_model=OrderRead)
def get_order(order_id: int, db: DB_Session) -> OrderRead:
    return get_one_order_or_404(order_id, db)


@router.post("", summary="Create an order", status_code=status.HTTP_201_CREATED, response_model=OrderRead)
def create_order(payload: OrderCreate, db: DB_Session) -> OrderRead:
    order = Order(user_id=payload.user_id)
    for item in payload.items:
        order.items.append(_materialize_item(item))

    try:
        db.add(order)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order.",
        ) from exc

    return reload_one_order(order.id, db)


@router.post("/{order_id}/items", summary="Add or replace an item", response_model=OrderRead)
def add_order_item(order_id: int, payload: OrderItemCreate, db: DB_Session) -> OrderRead:
    order = get_one_order_or_404(order_id, db)

    existing_item = next((item for item in order.items if item.product_id == payload.product_id), None)
    if existing_item is not None:
        existing_item.quantity = payload.quantity
        existing_item.unit_price = payload.unit_price
    else:
        order.items.append(_materialize_item(payload))

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to order.",
        ) from exc

    return reload_one_order(order_id, db)


@router.delete("/{order_id}/items/{product_id}", summary="Remove an item", response_model=OrderRead)
def remove_order_item(order_id: int, product_id: int, db: DB_Session) -> OrderRead:
    order = get_one_order_or_404(order_id, db)

    item = next((entry for entry in order.items if entry.product_id == product_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found for order.")

    try:
        db.delete(item)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from order.",
        ) from exc

    return reload_one_order(order_id, db)


@router.patch("/{order_id}", summary="Update an order", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: DB_Session) -> OrderRead:
    if payload.status is None and not payload.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update.")

    order = get_one_order_or_404(order_id, db)

    if payload.status is not None:
        order.status = payload.status

    if payload.items:
        by_product = {item.product_id: item for item in order.items}
        for item_update in payload.items:
            target = by_product.get(item_update.product_id)
            if target is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with product_id {item_update.product_id} not found in order.",
                )

            if item_update.quantity is None and item_update.unit_price is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No updates provided for product_id {item_update.product_id}.",
                )

            if item_update.quantity is not None:
                target.quantity = item_update.quantity
            if item_update.unit_price is not None:
                target.unit_price = item_update.unit_price

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order.",
        ) from exc

    return reload_one_order(order_id, db)


@router.delete("/{order_id}", summary="Delete an order", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: DB_Session) -> None:
    order = get_one_order_or_404(order_id, db)

    try:
        db.delete(order)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete order.",
        ) from exc


