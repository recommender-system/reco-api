import decimal
from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import Field, BaseModel, Extra


class BasicConsumableModel(BaseModel):
    """copied from reco-collector-api"""
    uid: str = Field(...)
    type: str = Field(...)
    name: str = Field(...)
    price: Optional[decimal.Decimal]
    url: Optional[str]
    image_url: Optional[str]
    update_time: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        # extra = Extra.allow  # for future changes: allow additional attributes for frontend
        schema_extra = {
            "example": {
                "uid": "12345",
                "type": "product",
                "name": "Garden Gnome Deluxe",
                "price": "19.99",
                "url": "https://path-to-consumable.com",
                "image_url": "https://path-to-consumable-image.com",
            }
        }