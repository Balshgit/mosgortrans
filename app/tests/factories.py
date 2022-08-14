import factory
from app.tests.models import User
from faker import Faker

faker = Faker('ru_RU')


class UserFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1000 + n)
    is_bot = False
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = faker.profile(fields=['username'])['username']
    language_code = 'ru'

    class Meta:
        model = User
