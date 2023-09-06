from __future__ import annotations
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from .author import Author
#     from .world import World
# else:
#     World = "World"
#     Author = "Author"

from dataclasses import dataclass, field
from typing import List

from strapi_model_mixin import StrapiModelMixin


class LinkedInProfile(StrapiModelMixin):
    id: str = None
    firstName: str = None
    lastName: str = None
    summary: str = None
    profileLink: str = None
    profilePicture: str = None
    createdAt: str = None
    updatedAt: str = None
    publishedAt: str = None
    model_path: str = "linked-in-profiles"
    # author: Author = None
    # worlds: List[World] = field(default_factory=list)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

        if self.profileLink is None:
            urn =  self.__dict__['entityUrn'].split(":")[3]
            urn = urn.replace("(", "")
            urn = urn.replace(")", "")
            self.__dict__['profileLink'] = f"https://www.linkedin.com/sales/lead/{urn}"
