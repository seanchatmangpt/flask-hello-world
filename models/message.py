from dataclasses import dataclass

from strapi_model_mixin import StrapiModelMixin


@dataclass
class Message(StrapiModelMixin):
    id: str = None
    content: str = None
    createdAt: str = None
    updatedAt: str = None
    publishedAt: str = None
    model_path: str = "messages"
