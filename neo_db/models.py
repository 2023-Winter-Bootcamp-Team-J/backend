from django.db import models

from neomodel import (StructuredNode, StringProperty, DateTimeProperty, RelationshipTo, RelationshipFrom,
                      UniqueIdProperty, BooleanProperty)


class Story(StructuredNode):
    story_id = UniqueIdProperty()
    content = StringProperty()
    createdAt = DateTimeProperty()
    updatedAt = DateTimeProperty()
    is_deleted = BooleanProperty()
    image_url = StringProperty()

    # 이야기는 여러 '자식' 분기를 가질 수 있고, 하나의 '부모' 분기를 가질 수 있음
    parent_story = RelationshipFrom('Story', 'BRANCHED_FROM')
    child_stories = RelationshipTo('Story', 'BRANCHES_TO')


# 사용자 정의 모델이 필요한 경우, 사용자를 모델링할 수 있음
class User(StructuredNode):
    user_id = UniqueIdProperty()
    nickname = StringProperty()
    createdAt = DateTimeProperty()
    updatedAt = DateTimeProperty()
    is_deleted = BooleanProperty()

    # 사용자가 작성한 스토리
    stories_written = RelationshipTo(Story, 'AUTHORED')

