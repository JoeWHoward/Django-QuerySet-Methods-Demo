from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key, related

from demo.models import *
from faker import Faker

class Command(BaseCommand):
    def handle(self, *args, **options):
        for x in range(150):
            baker.make_recipe("demo.rating_recipe")
            baker.make_recipe("demo.tag_recipe")
