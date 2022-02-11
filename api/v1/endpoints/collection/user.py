from typing import List

from fastapi import APIRouter, Depends, Body
import api.core.services.user as service_user
from motor.motor_asyncio import AsyncIOMotorClient

from api.core.db.models.item import BasicItemModel
from api.core.db.mongodb import get_database

from api.core.util.config import ENDPOINT_COLLECTION, ENDPOINT_USER, TAG_COLLECTION, TAG_USER

api_router = APIRouter(prefix=ENDPOINT_COLLECTION + ENDPOINT_USER, tags=[TAG_COLLECTION, TAG_USER])


@api_router.post("")
async def post_user(db: AsyncIOMotorClient = Depends(get_database),
                    item_models: List[BasicItemModel] = Body(...)):
    """Adds a single item model entry into database."""
    return await service_user.hello_user()