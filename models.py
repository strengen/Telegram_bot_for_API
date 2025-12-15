from peewee import (
    CharField,
    DateTimeField,
    IntegerField,
    Model,
    SqliteDatabase
)

from config import DB_PATH
from datetime import datetime

db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_name = CharField(null=True)
    registry_date = DateTimeField(default=datetime.now)

    def __str__(self):
        return (f'username: {self.username}, First Name: {self.first_name}, '
                f'Last Name: {self.last_name}, Registered: {self.registry_date}')

def create_models():
    db.create_tables(BaseModel.__subclasses__())
