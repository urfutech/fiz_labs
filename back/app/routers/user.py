from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas import User
from ..oauth2 import get_current_user_active


router = APIRouter()


@router.post("/login")
async def create_user()


# @router.get("/")
# async def read_items(
#     current_user: Annotated[User, Depends(get_current_user_active)],
# ) -> User:
#     return current_user
#
#
# @router.get("/")
# async def read_own_items(
#     current_user: Annotated[User, Depends(get_current_user_active)],
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]
