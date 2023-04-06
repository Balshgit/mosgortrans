import factory
from faker import Faker

from tests.data.models import Chat, User

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


class ChatFactory(factory.Factory):
    id = factory.Sequence(lambda n: 1 + n)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = faker.profile(fields=['username'])['username']
    type = 'private'

    class Meta:
        model = Chat
