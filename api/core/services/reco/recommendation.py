# "A recommendation is an item!"

import logging
import random
from typing import List

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
import api.core.util.config as cfg
from api.core.db.models.item import BasicItemModel

logger = logging.getLogger(__name__)


async def get_random_items(conn: AsyncIOMotorClient, n_recos=5, **kwargs) -> List[BasicItemModel]:
    """Retrieve random items from 'item' collection.
    Args:
        conn (AsyncIOMotorClient): Session object used for retrieving items from db.
        n_recos (int): Number of items that should be returned.
    Returns:
        List[BasicItemModel]: List of random items.
    """
    cursor = conn[cfg.DB_NAME][cfg.COLLECTION_NAME_ITEM].find()
    res = random.sample(await cursor.to_list(None), n_recos)
    res = [BasicItemModel(**i) for i in res]
    return limit_returned_items(res, n_recos)


async def get_latest_items(conn: AsyncIOMotorClient, n_recos=5, **kwargs) -> List[BasicItemModel]:
    """Retrieve the latest items from 'item' collection.
    Args:
        conn (AsyncIOMotorClient): Session object used for retrieving items from db.
        n_recos (int): Number of items that should be returned.
    Returns:
        List[BasicItemModel]: List of random items.
    """
    cursor = conn[cfg.DB_NAME][cfg.COLLECTION_NAME_ITEM] \
        .find() \
        .sort([('created_time', pymongo.DESCENDING)])
    res = await cursor.to_list(n_recos)  # TODO: check if this returns sorted products of all or n_reco documents
    res = [BasicItemModel(**i) for i in res]
    return limit_returned_items(res, n_recos)


async def get_collaborative_filtering_items(conn: AsyncIOMotorClient,
                                            item_id_seed: int,
                                            base: str,
                                            n_recos=5) -> List[BasicItemModel]:
    """Retrieve item based collaborative filtered items from 'relation' db.
    Args:
        conn (AsyncIOMotorClient): Session object used for retrieving items from db.
        item_id_seed (int): ID of seed item that is used for finding similar items.
        base (str): Type of filtering, i.e. "item" or "used".
        n_recos (int): Number of items that should be returned.
    Returns:
        List[BasicItemModel]: List of similar (item-wise) items.
    """
    res = []
    pipeline = [
        {'$match': {
            'item_id_seed': str(quick_fix_adjust_item_id(item_id_seed)),
            'base': base
        }},
        {
            '$lookup': {
                'from': cfg.COLLECTION_NAME_ITEM,
                'localField': 'item_id_recommended',
                'foreignField': 'id',
                'as': 'item'
            }
        },
        {'$unwind': '$item'},  # reduces and flattens the item (array) to a single object
        {'$sort': {'similarity': -1}},
        {'$limit': n_recos}
    ]
    async for doc in conn[cfg.DB_NAME][cfg.COLLECTION_NAME_RELATIONS].aggregate(pipeline):
        res.append(BasicItemModel(**doc['item']))
    return limit_returned_items(res, n_recos)


def quick_fix_adjust_item_id(item_id: int):
    """ quick fix for variants """
    if len(str(item_id)) > 4:
        item_id = str(item_id)[:-3]
    return int(item_id)


def limit_returned_items(items, n_recos) -> List[BasicItemModel]:
    """ This function should take care of adding items when len(items) < n_recos """
    # TODO: it does not limit but add items if necessary
    if len(items) < n_recos:
        logging.warning(
            f"Number of requested items ({n_recos}) less than number of items ({len(items)}) in database")
    return items[0:n_recos]


reco_str2fun = {
    cfg.TYPE_FALLBACK: get_random_items,
    cfg.TYPE_ITEM_BASED_COLLABORATIVE_FILTERING: get_collaborative_filtering_items,
    cfg.TYPE_LATEST: get_latest_items,
    cfg.TYPE_RANDOM_RECOMMENDATIONS: get_random_items
}
