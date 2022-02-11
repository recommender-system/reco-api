import logging
from fastapi import Request

from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi import status
from pydantic import ValidationError
from starlette.responses import JSONResponse

import api.core.util.config as cfg
from motor.motor_asyncio import AsyncIOMotorClient

from api.core.db.models.evidence import BasicEvidenceModel

logger = logging.getLogger(__name__)


async def create_evidence(conn: AsyncIOMotorClient, evidence_models: List[BasicEvidenceModel]):
    """Inserts collection object(s) to db.

    Returns:
        JSONResponse: Status of insert command.
    """
    t = conn[cfg.DB_NAME][cfg.COLLECTION_NAME_EVIDENCE]
    await t.insert_many([jsonable_encoder(e, exclude_none=True) for e in evidence_models])
    return JSONResponse(status_code=status.HTTP_201_CREATED)


def add_evidence_model_to_list(evidence_list: List, req: Request, o: dict):
    try:
        evidence_list.append(BasicEvidenceModel(**o,
                                                req_headers=req.headers,
                                                req_client=req.client,
                                                req_cookies=req.cookies))
    except ValidationError as e:
        logger.warning(f"Invalid object provided in collection list:{o}", e)


async def process_evidence(request: Request) -> List[BasicEvidenceModel]:
    json = await request.json()
    evidence_list = []
    if isinstance(json, list):
        for o in json:
            add_evidence_model_to_list(evidence_list, request, o)
    elif isinstance(json, dict):
        add_evidence_model_to_list(evidence_list, request, json)
    return evidence_list

# async def get_all_evidence(conn: AsyncIOMotorClient) -> List[BasicEvidenceModel]:
#     """Returns all objects from collection collection, regardless if they represent an collection object.
#
#     This method will throw an error when object different to EvidenceModel are persisted in collection collection.
#
#     Returns:
#         List[BasicEvidenceModel]: Complete list of collection entries in collection collection.
#     """
#     cursor = conn[cfg.DB_NAME][cfg.COLLECTION_NAME_EVIDENCE].find()
#     evidence = await cursor.to_list(None)
#     return evidence
