import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    dir_data = f"{settings.BASE_DIR}/data"

    def load_tags(self):
        with open(f"{self.dir_data}/tags.csv", encoding="utf-8") as file:
            Tag.objects.all().delete()
            reader = csv.DictReader(file)
            Tag.objects.bulk_create([Tag(**data) for data in reader])
        self.stdout.write(self.style.SUCCESS("Все теги загружены!"))

    def load_ingredients(self):
        with open(
            f"{self.dir_data}/ingredients.csv", encoding="utf-8"
        ) as file:
            Ingredient.objects.all().delete()
            reader = csv.DictReader(
                file, fieldnames=["name", "measurement_unit"]
            )
            Ingredient.objects.bulk_create(
                [Ingredient(**data) for data in reader]
            )
        self.stdout.write(self.style.SUCCESS("Все ингредиенты загружены!"))

    def handle(self, *args, **options):
        self.load_tags()
        self.load_ingredients()
