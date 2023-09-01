from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .blog import Blog
    from .message import Message
    from .author import Author
else:
    Blog = "Blog"
    Message = "Message"
    Author = "Author"

from dataclasses import dataclass, field
from typing import List

from strapi_model_mixin import StrapiModelMixin


@dataclass
class World(StrapiModelMixin):
    id: str = None
    guid: str = None
    intro: str = None
    createdAt: str = None
    updatedAt: str = None
    publishedAt: str = None
    model_path: str = "worlds"
    blogs: List[Blog] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)
    author: Author = None
