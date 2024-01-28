import os
import traceback
import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда для импорта ингредиентов из CSV-файла.
    """
    def load_data_from_csv(self, filename, model_class):
        """
        Функция удаляет все объекты модели Ingredient,
        если база уже заполнена.
        """
        if Ingredient.objects.exists():
            Ingredient.objects.all().delete()
        """
        Функция для импорта данных из CSV-файла.
        """
        try:
            with open(
                os.path.join(settings.BASE_DIR, 'data', filename),
                encoding='utf-8'
            ) as file:
                reader = csv.reader(file)
                for row in reader:
                    name, measurement_unit = row
                    model_instance = model_class(
                        name=name,
                        measurement_unit=measurement_unit
                    )
                    model_instance.save()
        except ValueError:
            print('Некорректное значение в данных')
        except Exception:
            raise

    def handle(self, *args, **options,):
        """
        Выводит сообщение о статусе импорта данных.
        """
        try:
            self.load_data_from_csv(
                'ingredients.csv',
                Ingredient
            )
            print('Импорт данных завершен.')
        except Exception:
            traceback.print_exc()
            print('Импорт данных не удался.')
