from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key, related

from demo.models import *
from faker import Faker

fake = Faker()

address_recipe = Recipe(
    Address,
    street=fake.street_name(),
    street_number=fake.building_number(),
    zip_code=fake.postcode(),
    city=fake.city(),
    state=fake.state(),
)

person_recipe = Recipe(
    Person,
    name=fake.name(),
    occupation=fake.job(),
    address=foreign_key(address_recipe),
)

title_recipe = Recipe(
    Title,
    text=fake.sentence(nb_words=6)
)

book_recipe = Recipe(
    Book,
    author=foreign_key(person_recipe),
    title=foreign_key(title_recipe),
)

tag_recipe = Recipe(
    Tag,
    related_books=related(book_recipe)
)

rating_recipe = Recipe(
    Rating,
    target=foreign_key(book_recipe)
)