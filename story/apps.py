from contextlib import contextmanager
from django.apps import AppConfig
from neo4j import GraphDatabase

class StoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'story'


