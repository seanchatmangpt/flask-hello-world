from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import World
else:
    World = "World"

from dataclasses import dataclass, field

from typing import List

from strapi_model_mixin import StrapiModelMixin


@dataclass
class Author(StrapiModelMixin):
    id: str = None
    name: str = None
    email: str = None
    avatar: str = None
    createdAt: str = None
    updatedAt: str = None
    publishedAt: str = None
    articles: list = field(default_factory=list)
    worlds: List[World] = field(default_factory=list)
    model_path: str = "authors"
