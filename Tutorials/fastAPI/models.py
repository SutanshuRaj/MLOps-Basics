from mongoengine import Document, StringField, IntField, ListField

class Employee(Document):
    name = StringField(max_length = 32)
    age = IntField()
    teams = ListField()
    emp_id = IntField()

class Admin(Document):
    username = StringField()
    password = StringField()


