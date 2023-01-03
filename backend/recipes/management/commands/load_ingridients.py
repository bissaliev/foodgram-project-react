import csv

from django.conf import settings
from django.core.management import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.DictReader(file, fieldnames=['name', 'measurement_unit'])
            Ingredient.objects.bulk_create(
                [Ingredient(**data) for data in reader]
            )
        self.stdout.write(self.style.SUCCESS('Все ингредиенты загружены!'))
