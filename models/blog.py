from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .author import Author
    from .world import World
else:
    World = "World"
    Author = "Author"

from dataclasses import dataclass, field
from typing import List

from strapi_model_mixin import StrapiModelMixin


@dataclass
class Blog(StrapiModelMixin):
    id: str = None
    text: str = None
    createdAt: str = None
    updatedAt: str = None
    publishedAt: str = None
    model_path: str = "blogs"
    author: Author = None
    worlds: List[World] = field(default_factory=list)
