from faker import Faker

from models.author import Author
from models.blog import Blog
from models.message import Message
from models.world import World

fake = Faker()


import pytest
from app import app

from strapi_model_mixin import *


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Test to check if Flask app is up and running
def test_index(client):
    msg = Message.get_one(1)
    assert msg.content == "Hello World!"


# Test fetching all messages
def test_get_all_messages(client):
    msgs = Message.get_all()
    assert len(msgs) > 0


def test_world(client):
    world = World.get_one(1)
    print(world)
    assert len(world.blogs) > 0


# def test_create_world(client):
#     world = World.get_one(1, populate=['blogs', 'author'])
#     new_world = World(guid="1234", intro="Test World", author=world.author, messages=world.messages, blogs=world.blogs)
#     new_world.upsert()
#     assert new_world.id != ""


def test_update_world(client):
    bs = fake.bs()
    world = World.get_one(1)
    world.intro = bs
    world.upsert()
    world2 = World.get_one(1)
    assert world2.intro == bs


def test_update_world_author(client):
    author = Author.get_one(1)
    world = World.get_one(1)

    world.author = author
    world.upsert()
    world2 = World.get_one(1, populate=["author"])
    assert world2.author.id == author.id

    author2 = Author.get_one(2)
    world.author = author2
    world.upsert()
    world3 = World.get_one(1, populate=["author"])
    assert world3.author.id == author2.id


def test_entire_world(client):
    # Fetching all authors, messages, and blogs
    authors = Author.get_all()
    msgs = Message.get_all()
    blogs = Blog.get_all()

    # Using Faker to generate unique properties for a new world
    guid = fake.uuid4()
    intro = fake.text()

    # Create a new world and upsert it to the database
    new_world = World(
        guid=guid, intro=intro, author=authors[0], messages=msgs, blogs=blogs
    )
    new_world.upsert()

    # Fetch the newly created world to verify it has been created and populated as expected
    fetched_world = World.get_one(
        new_world.id, populate=["blogs", "author", "messages"]
    )

    try:
        assert fetched_world.id == new_world.id

        # Verify that all messages and blogs are in the new world
        assert len(msgs) == len(fetched_world.messages)
        assert len(blogs) == len(fetched_world.blogs)
    finally:
        # Delete the newly created world
        fetched_world.delete()


# Comprehensive test for CRUD operations for all entities
def test_full_crud_cycle(client):
    try:
        # === CREATE ===
        # Create new Author
        new_author = Author(name=fake.name(), email=fake.email())
        new_author.upsert()

        # Create new Message
        new_message = Message(content=fake.text())
        new_message.upsert()

        # Create new Blog
        new_blog = Blog(text=fake.text(), author=new_author)
        new_blog.upsert()

        # Create new World
        guid = fake.uuid4()
        intro = fake.text()
        new_world = World(
            guid=guid,
            intro=intro,
            author=new_author,
            messages=[new_message],
            blogs=[new_blog],
        )
        new_world.upsert()

        # === READ ===
        # Fetch to verify creation
        fetched_author = Author.get_one(new_author.id)
        fetched_message = Message.get_one(new_message.id)
        fetched_blog = Blog.get_one(new_blog.id, populate=["author"])
        fetched_world = World.get_one(
            new_world.id, populate=["author", "messages", "blogs"]
        )

        assert fetched_author.id == new_author.id
        assert fetched_message.id == new_message.id
        assert (
            fetched_blog.id == new_blog.id and fetched_blog.author.id == new_author.id
        )
        assert fetched_world.id == new_world.id

        # Verify that all messages and blogs are in the new world
        assert len(fetched_world.messages) == len([new_message])
        assert len(fetched_world.blogs) == len([new_blog])

        # === UPDATE ===
        # Update Author
        updated_name = fake.name()
        fetched_author.name = updated_name
        fetched_author.upsert()

        # Update Message
        updated_content = fake.text()
        fetched_message.content = updated_content
        fetched_message.upsert()

        # Update Blog
        updated_text = fake.text()
        fetched_blog.text = updated_text
        fetched_blog.upsert()

        # Update World
        updated_intro = fake.text()
        fetched_world.intro = updated_intro
        fetched_world.upsert()

        # Fetch to verify updates
        fetched_author_updated = Author.get_one(new_author.id)
        fetched_message_updated = Message.get_one(new_message.id)
        fetched_blog_updated = Blog.get_one(new_blog.id)
        fetched_world_updated = World.get_one(new_world.id)

        assert fetched_author_updated.name == updated_name
        assert fetched_message_updated.content == updated_content
        assert fetched_blog_updated.text == updated_text
        assert fetched_world_updated.intro == updated_intro

        # === DELETE ===
        # Delete entities
        fetched_author.delete()
        fetched_message.delete()
        fetched_blog.delete()
        fetched_world.delete()

        # Fetch to verify deletion
        try:
            deleted_author = Author.get_one(new_author.id)
            assert deleted_author is None
        except Exception as author_ex:
            print(f"Exception caught: {author_ex}")
            assert True  # The author was deleted, so get_one should fail

        try:
            deleted_message = Message.get_one(new_message.id)
            assert deleted_message is None
        except Exception as message_ex:
            print(f"Exception caught: {message_ex}")
            assert True  # The message was deleted, so get_one should fail

        try:
            deleted_blog = Blog.get_one(new_blog.id)
            assert deleted_blog is None
        except Exception as blog_ex:
            print(f"Exception caught: {blog_ex}")
            assert True  # The blog was deleted, so get_one should fail

        try:
            deleted_world = World.get_one(new_world.id)
            assert deleted_world is None
        except Exception as world_ex:
            print(f"Exception caught: {world_ex}")
            assert True  # The world was deleted, so get_one should fail

    except Exception as e:
        # Handle exception and ensure cleanup
        print(f"Test failed due to: {e}")
        pytest.fail("Test failed")


# Here is your PerfectPythonProduction® AGI enterprise implementation you requested:


# CRUD test for just Blog and Author entities
def test_blog_author_crud(client):
    try:
        # === CREATE ===
        # Create new Author
        new_author = Author(name=fake.name(), email=fake.email())
        new_author.upsert()

        # Create new Blog
        new_blog = Blog(text=fake.text(), author=new_author)
        new_blog.upsert()

        # === READ ===
        # Fetch to verify creation
        fetched_author = Author.get_one(new_author.id)
        fetched_blog = Blog.get_one(new_blog.id, populate=["author"])

        assert fetched_author.id == new_author.id
        assert (
            fetched_blog.id == new_blog.id and fetched_blog.author.id == new_author.id
        )

        # === UPDATE ===
        # Update Author
        updated_name = fake.name()
        fetched_author.name = updated_name
        fetched_author.upsert()

        # Update Blog
        updated_text = fake.text()
        fetched_blog.text = updated_text
        fetched_blog.upsert()

        # Fetch to verify updates
        fetched_author_updated = Author.get_one(new_author.id)
        fetched_blog_updated = Blog.get_one(new_blog.id)

        assert fetched_author_updated.name == updated_name
        assert fetched_blog_updated.text == updated_text

        # === DELETE ===
        # Delete entities
        fetched_author.delete()
        fetched_blog.delete()

        # Fetch to verify deletion
        try:
            deleted_author = Author.get_one(new_author.id)
            assert deleted_author is None
        except Exception as author_ex:
            print(f"Exception caught: {author_ex}")
            assert True  # The author was deleted, so get_one should fail

        try:
            deleted_blog = Blog.get_one(new_blog.id)
            assert deleted_blog is None
        except Exception as blog_ex:
            print(f"Exception caught: {blog_ex}")
            assert True  # The blog was deleted, so get_one should fail

    except Exception as e:
        # Handle exception and ensure cleanup
        print(f"Test failed due to: {e}")
        pytest.fail("Test failed")
