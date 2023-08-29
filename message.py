from dataclasses import dataclass

from strapi_model_mixin import StrapiModelMixin


@dataclass
class Message(StrapiModelMixin):
    id: str = ""
    content: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    publishedAt: str = ""
    model_path: str = "messages"
