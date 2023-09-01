from __future__ import annotations

import json
import logging
from abc import abstractmethod
from functools import partial

from dotenv import load_dotenv
from flask import Flask, request
from typing import Dict, Type, Optional, TypeVar, List, Union, get_type_hints
import os

from pystrapi import StrapiClientSync, PublicationState
from pystrapi.types import (
    StrapiEntriesResponse,
    StrapiEntryResponse,
    PopulationParameter,
    PaginationParameter,
)

class_registry = {}

# Load environment variables
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API URL and token from environment variables
api_url = os.getenv("STRAPI_API_URL", "https://strapi-27bu.onrender.com/api/")
api_token = os.getenv(
    "STRAPI_API_TOKEN",
    "d81f6b816636e69d7429d3dfd5e8330bea1e3b7a35c7c69b80b250398d957358883b9547e1e4f97bf06c490a5802d51194311b7ea5718155e4aa9ab177f415dca41648cee9b1a74c577dac99fb3eff2de0b2d3633a6172bacfe76b2ec6299d2bdeb5dee3ddebd0928518bd51c77cab032be17271b316ca0ca33640821433af4a",
)


def convert_filters_to_dict(filter_str):
    """
    Converts a string of filters into a Python dictionary.
    """
    if not filter_str:
        return None
    try:
        # If there's an equal sign, wrap the string in curlies to form a valid JSON object
        if "=" in filter_str:
            filter_str = '{"' + filter_str + "}"

        # Replace the equal sign with a colon for JSON compatibility
        filter_str = filter_str.replace("=", '":')

        # Replace single quotes with double quotes for JSON compatibility
        json_compatible_str = filter_str.replace("'", '"')

        # Parse the JSON-compatible string into a Python dictionary
        return json.loads(json_compatible_str)

    except json.JSONDecodeError:
        # Handle parsing exceptions
        logger.error(
            f"An error occurred while converting filters string to dict: Invalid string {filter_str}"
        )
        return None


class StrapiClient:
    _instance: StrapiClientSync = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("Initializing StrapiClientSync instance.")
            cls._instance = StrapiClientSync(api_url=api_url, token=api_token)
        return cls._instance


class StrapiModelMixin:
    pass


T = TypeVar("T", bound=StrapiModelMixin)


class StrapiModelMixin:
    client: StrapiClientSync = StrapiClient()  # Reference to StrapiClientSync instance

    @property
    @abstractmethod
    def model_path(self) -> str:
        """Abstract method to be implemented by subclasses to provide the model path."""
        pass

    @classmethod
    def get_one(
        cls: Type[T],
        _id: str | int,
        populate: Optional[PopulationParameter] = "*",
        fields: Optional[List[str]] = None,
        **kwargs,
    ) -> Optional[T]:
        response = cls.fetch_one(_id, populate, fields)
        if response:
            try:
                obj = cls(**response["data"]["attributes"])
                obj.id = response["data"]["id"]
                cls._populate_relationships(obj)
                return obj
            except Exception as e:
                logger.error(f"An error occurred while parsing response: {e}")
                return None
        return None

    @classmethod
    def _extract_relationships(cls) -> Dict[str, Type]:
        relationships = {}
        type_hints = get_type_hints(cls)

        for field_name, type_hint in type_hints.items():
            # If the type hint is a string, get_type_hints would have resolved it
            if hasattr(type_hint, "__origin__") and issubclass(
                type_hint.__origin__, list
            ):
                type_argument = type_hint.__args__[0]
                relationships[field_name] = class_registry[type_hint.__args__[0].__forward_arg__]
            # if it is a forward reference, we need to resolve it
            elif hasattr(type_hint, "__forward_arg__"):
                relationships[field_name] = class_registry[type_hint.__forward_arg__]

        return relationships

    @classmethod
    def _populate_relationships(cls, obj):
        for rel_name, rel_cls in cls._extract_relationships().items():
            print(rel_name, rel_cls)
            inst_list = []
            rel_attr = getattr(obj, rel_name)
            if rel_attr is None:
                continue
            if isinstance(rel_attr, list) and len(getattr(obj, rel_name)) == 0:
                continue
            if isinstance(rel_attr.get("data"), dict):
                rel_inst = rel_cls(**rel_attr["data"]["attributes"])
                rel_inst.id = rel_attr["data"]["id"]
                setattr(obj, rel_name, rel_inst)
                continue
            if getattr(obj, rel_name)["data"] is not None:
                for data in getattr(obj, rel_name)["data"]:
                    rel_inst = rel_cls(**data["attributes"])
                    rel_inst.id = data["id"]
                    inst_list.append(rel_inst)
            setattr(obj, rel_name, inst_list)

    @classmethod
    def get_all(
        cls: Type[T],
        sort: Optional[List[str]] = None,
        filters: Optional[dict] = None,
        populate: Optional[PopulationParameter] = "*",
        fields: Optional[List[str]] = None,
        pagination: Optional[PaginationParameter] = None,
        publication_state: Optional[Union[str, PublicationState]] = None,
        get_all: bool = False,
        batch_size: int = 100,
        **kwargs,
    ) -> List[T]:
        responses = cls.fetch_all(
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            pagination=pagination,
            publication_state=publication_state,
            get_all=get_all,
            batch_size=batch_size,
            **kwargs,
        )
        if responses:
            objs = []
            for response in responses["data"]:
                obj = cls(**response["attributes"])
                obj.id = response["id"]
                cls._populate_relationships(obj)
                objs.append(obj)
            return objs
        return []

    def upsert(self, **kwargs) -> bool:
        excluded_attrs = [
            "createdAt",
            "updatedAt",
            "publishedAt",
            "model_path",
            "model_paths",
        ]
        data = {
            attr: getattr(self, attr)
            for attr in self.__annotations__
            if attr not in excluded_attrs
        }
        data.update(kwargs)
        response = {}

        if hasattr(self, "id") and getattr(self, "id") is not None:
            _id = data.pop("id")
            response = self.update(_id, data)
        else:
            response = self.create(data)

        if response:
            # Update object with response data, the id is in the response["data"]["id"] field
            setattr(self, "id", response["data"]["id"])
            for attr, value in response["data"]["attributes"].items():
                setattr(self, attr, value)
            return True
        return False

    def delete(self) -> bool:
        if hasattr(self, "id") and getattr(self, "id") is not None:
            _id = getattr(self, "id")
            response = self.__class__.delete_one(_id)
            if response:
                return True
        return False

    @classmethod
    def _extract_request_args(cls):
        """
        Helper function to extract request arguments and set them to None if not provided.
        """
        filters = None
        if request.args.get("filters"):
            convert_filters_to_dict(request.args.get("filters"))
        args = {
            "sort": request.args.getlist("sort") if request.args.get("sort") else None,
            "filters": filters if request.args.get("filters") else None,
            "populate": request.args.get("populate")
            if request.args.get("populate")
            else None,
            "fields": request.args.getlist("fields")
            if request.args.get("fields")
            else None,
            "pagination": json.loads(request.args.get("pagination"))
            if request.args.get("pagination")
            else None,
            "publication_state": request.args.get("publication_state")
            if request.args.get("publication_state")
            else None,
            "_id": request.args.get("id") if request.args.get("id") else None,
            "get_all": bool(request.args.get("get_all"))
            if request.args.get("get_all")
            else None,
        }
        if request.data:
            args["data"] = json.loads(request.data)
        return args

    @classmethod
    def fetch_all(
        cls,
        sort: Optional[List[str]] = None,
        filters: Optional[dict] = None,
        populate: Optional[PopulationParameter] = None,
        fields: Optional[List[str]] = None,
        pagination: Optional[PaginationParameter] = None,
        publication_state: Optional[Union[str, PublicationState]] = None,
        get_all: bool = False,
        batch_size: int = 100,
        **kwargs,
    ) -> StrapiEntriesResponse:
        logger.info(f"Fetching all entries from {cls.model_path}")
        response = cls.client.get_entries(
            plural_api_id=str(cls.model_path),
            sort=sort,
            filters=filters,
            populate=populate,
            fields=fields,
            pagination=pagination,
            publication_state=publication_state,
            get_all=get_all,
            batch_size=batch_size,
        )
        logger.debug(f"Retrieved {len(response)} entries from {cls.model_path}")
        return response

    @classmethod
    def fetch_one(
        cls,
        _id: str | int,
        populate: Optional[PopulationParameter] = None,
        fields: Optional[List[str]] = None,
        **kwargs,
    ) -> StrapiEntryResponse:
        logger.info(f"Fetching entry with ID {_id} from {cls.model_path}")

        response = cls.client.get_entry(
            plural_api_id=str(cls.model_path),
            document_id=int(_id),
            populate=populate,
            fields=fields,
        )
        logger.debug(f"Retrieved entry from {cls.model_path}: {response}")
        return response

    @classmethod
    def create(cls, data: Dict, **kwargs) -> Dict:
        logger.info(f"Creating entry in {cls.model_path} with data: {data}")
        # Replace relationships with their IDs
        cls._replace_relationships_with_ids(data)
        response = cls.client.create_entry(plural_api_id=str(cls.model_path), data=data)
        logger.debug(f"Created entry in {cls.model_path}: {response}")
        return response

    @classmethod
    def _replace_relationships_with_ids(cls, data):
        relationships = cls._extract_relationships()
        for rel_name, rel_cls in relationships.items():
            if rel_name in data:
                if data[rel_name] is None:
                    continue
                elif isinstance(data[rel_name], list):
                    # If all the are dicts, then don't do anything
                    if all(isinstance(item, dict) for item in data[rel_name]):
                        continue
                    data[rel_name] = [
                        {"id": getattr(rel_obj, "id")} for rel_obj in data[rel_name]
                    ]
                else:
                    # If it's a dict, then don't do anything
                    if isinstance(data[rel_name], dict):
                        continue
                    data[rel_name] = {"id": getattr(data[rel_name], "id")}

    @classmethod
    def update(cls, _id: str | int, data: Dict, **kwargs) -> Dict:
        logger.info(
            f"Updating entry with ID {_id} in {cls.model_path} with data: {data}"
        )
        cls._replace_relationships_with_ids(data)
        response = cls.client.update_entry(
            plural_api_id=str(cls.model_path), document_id=int(_id), data=data
        )
        logger.debug(f"Updated entry in {cls.model_path}: {response}")
        return response

    @classmethod
    def delete_one(cls, _id: str | int, **kwargs) -> Dict:
        logger.info(f"Deleting entry with ID {_id} from {cls.model_path}")
        response = cls.client.delete_entry(
            plural_api_id=str(cls.model_path), document_id=int(_id)
        )
        logger.debug(f"Deleted entry from {cls.model_path}: {response}")
        return response

    @classmethod
    def fetch_all_route(cls):
        args = cls._extract_request_args()
        return cls.fetch_all(**args)

    @classmethod
    def fetch_one_route(cls, _id: str | int):
        args = cls._extract_request_args()
        args["_id"] = _id
        return cls.fetch_one(**args)

    @classmethod
    def create_route(cls):
        args = cls._extract_request_args()
        return cls.create(**args)

    @classmethod
    def update_route(cls, _id: str | int):
        args = cls._extract_request_args()
        args["_id"] = _id
        return cls.update(**args)

    @classmethod
    def delete_route(cls, _id: str | int):
        args = cls._extract_request_args()
        args["_id"] = _id
        return cls.delete_one(**args)

    @classmethod
    def add_routes(cls, app: Flask) -> None:
        class_registry[cls.__name__] = cls
        model_name = cls.model_path

        app.add_url_rule(
            f"/{model_name}",
            f"{model_name}_all",
            partial(cls.fetch_all_route),
            methods=["GET"],
        )
        app.add_url_rule(
            f"/{model_name}/<string:_id>",
            f"{model_name}_one",
            partial(cls.fetch_one_route),
            methods=["GET"],
        )
        app.add_url_rule(
            f"/{model_name}",
            f"{model_name}_create",
            partial(cls.create_route),
            methods=["POST"],
        )
        app.add_url_rule(
            f"/{model_name}/<string:_id>",
            f"{model_name}_update",
            partial(cls.update_route),
            methods=["PUT"],
        )
        app.add_url_rule(
            f"/{model_name}/<string:_id>",
            f"{model_name}_delete",
            partial(cls.delete_route),
            methods=["DELETE"],
        )


# if __name__ == "__main__":
# msg = Message(content="Hello World2!")
# msg.upsert()
# msgs = Message.get_all(pagination={"limit": 1}, sort=["createdAt"])
# msg = Message.get_one("1")
# print(world)
