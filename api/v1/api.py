from fastapi import APIRouter

from api.v1.collection import user, item, evidence
from api.v1.recommendations import item_based
from api.v1.recommendations import a_b_testing

api_router = APIRouter()

# Collection router
api_router.include_router(evidence.api_router)
api_router.include_router(item.api_router)
api_router.include_router(user.api_router)

# Recommendation router
api_router.include_router(item_based.api_router)
api_router.include_router(a_b_testing.api_router)
