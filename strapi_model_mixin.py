import logging
from dotenv import load_dotenv
from flask import jsonify, Flask, request
from typing import Dict, Type, Optional, TypeVar, List
import os

from pystrapi import StrapiClientSync
from pystrapi.types import StrapiEntriesResponse, StrapiEntryResponse

# Load environment variables
load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API URL and token from environment variables
api_url = os.getenv("STRAPI_API_URL", "https://strapi-27bu.onrender.com/api/")
api_token = os.getenv("STRAPI_API_TOKEN",
                      "d81f6b816636e69d7429d3dfd5e8330bea1e3b7a35c7c69b80b250398d957358883b9547e1e4f97bf06c490a5802d51194311b7ea5718155e4aa9ab177f415dca41648cee9b1a74c577dac99fb3eff2de0b2d3633a6172bacfe76b2ec6299d2bdeb5dee3ddebd0928518bd51c77cab032be17271b316ca0ca33640821433af4a")


class StrapiClient:
    _instance: StrapiClientSync = None

    def __new__(cls):
        if cls._instance is None:
            logger.info('Initializing StrapiClientSync instance.')
            cls._instance = StrapiClientSync(api_url=api_url, token=api_token)
        return cls._instance


class StrapiModelMixin:
    pass


T = TypeVar("T", bound=StrapiModelMixin)


class StrapiModelMixin:
    client: StrapiClientSync = StrapiClient()  # Reference to StrapiClientSync instance

    @classmethod
    def get_one(cls: Type[T], _id: str, **kwargs) -> Optional[T]:
        response = cls.fetch_one(_id, **kwargs)
        if response:
            obj = cls(**response["data"]["attributes"])
            obj.id = response["data"]["id"]
            return obj
        return None

    @classmethod
    def get_all(cls: Type[T], **kwargs) -> List[T]:
        responses = cls.fetch_all(**kwargs)
        if responses:
            objs = []
            for response in responses["data"]:
                obj = cls(**response["attributes"])
                obj.id = response["id"]
                objs.append(obj)
            return objs
        return []

    @property
    def model_path(self) -> str:
        raise NotImplementedError("Subclasses must define a model_path property")

    def upsert(self, **kwargs) -> bool:
        excluded_attrs = ["id", "createdAt", "updatedAt", "publishedAt", "model_path", "model_paths"]
        data = {attr: getattr(self, attr) for attr in self.__annotations__ if attr not in excluded_attrs}
        data.update(kwargs)
        response = {}

        if "id" in data:
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

    @classmethod
    def fetch_all(cls, **kwargs) -> StrapiEntriesResponse:
        logger.info(f"Fetching all entries from {cls.model_path} with parameters {kwargs}")
        response = cls.client.get_entries(plural_api_id=str(cls.model_path), **kwargs)
        logger.debug(f"Retrieved {len(response)} entries from {cls.model_path}")
        return response

    @classmethod
    def fetch_one(cls, _id: str, **kwargs) -> StrapiEntryResponse:
        logger.info(f"Fetching entry with ID {_id} from {cls.model_path}")
        response = cls.client.get_entry(plural_api_id=str(cls.model_path), document_id=_id, **kwargs)
        logger.debug(f"Retrieved entry from {cls.model_path}: {response}")
        return response

    @classmethod
    def create(cls, data: Dict, **kwargs) -> Dict:
        logger.info(f"Creating entry in {cls.model_path} with data: {data}")
        response = cls.client.create_entry(plural_api_id=str(cls.model_path), data=data)
        logger.debug(f"Created entry in {cls.model_path}: {response}")
        return response

    @classmethod
    def update(cls, _id: str, data: Dict, **kwargs) -> Dict:
        logger.info(f"Updating entry with ID {_id} in {cls.model_path} with data: {data}")
        response = cls.client.update_entry(plural_api_id=str(cls.model_path), document_id=_id, data=data)
        logger.debug(f"Updated entry in {cls.model_path}: {response}")
        return response

    @classmethod
    def delete(cls, _id: str, **kwargs) -> Dict:
        logger.info(f"Deleting entry with ID {_id} from {cls.model_path}")
        response = cls.client.delete_entry(plural_api_id=str(cls.model_path), document_id=_id)
        logger.debug(f"Deleted entry from {cls.model_path}: {response}")
        return response

    def add_routes(self, app: Flask, model_class) -> None:
        model_inst = model_class()

        @app.route(f"/{model_inst.model_path}", methods=["GET"])
        def fetch_all():
            logger.info(f"Fetching all entries from {model_inst.model_path}")
            entities = model_inst.fetch_all(**request.args.to_dict())
            return jsonify(entities)

        @app.route(f"/{model_inst.model_path}/<int:_id>", methods=["GET"])
        def fetch_one(_id: str):
            logger.info(f"Fetching entry with ID {_id} from {model_inst.model_path}")
            model = model_inst.fetch_one(_id, **request.args.to_dict())
            return jsonify(model)

        @app.route(f"/{model_inst.model_path}", methods=["POST"])
        def create():
            logger.info(f"Creating entry in {model_inst.model_path} with data: {request.json}")
            response = model_inst.create(request.json, **request.args.to_dict())
            return jsonify(response), 201

        @app.route(f"/{model_inst.model_path}/<int:_id>", methods=["PUT"])
        def update(_id: str):
            logger.info(f"Updating entry with ID {_id} in {model_inst.model_path} with data: {request.json}")
            response = model_inst.update(_id, request.json, **request.args.to_dict())
            return jsonify(response)

        @app.route(f"/{model_inst.model_path}/<int:_id>", methods=["DELETE"])
        def delete(_id: str):
            logger.info(f"Deleting entry with ID {_id} from {model_inst.model_path}")
            response = model_inst.delete(_id, **request.args.to_dict())
            return jsonify(response)
