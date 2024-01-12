# load_neo4j_data.py
import json
from neo4j import GraphDatabase
import os


def load_data_to_neo4j(file_path):
    # Neo4j 데이터베이스 연결 설정
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "nextpage"

    # 파일에서 데이터 로드
    with open(file_path, 'r') as file:
        #data = json.load(file)
        data = [
            # # 사용자 데이터
            # {
            #     "model": "user.User",
            #     "fields": {
            #         "user_id": "unique-user-id-001",
            #         "nickname": "Kanguk",
            #         "created_at": "2024-01-08T06:39:55.329190",
            #         "updated_at": "2024-01-08T06:39:55.329261",
            #         "is_deleted": False
            #     }
            # },
            # 스토리 데이터
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-001",
                    "content": "이것은 최초의 스토리 내용입니다.",
                    "created_at": "2024-01-08T07:00:00.000000",
                    "updated_at": "2024-01-08T07:00:00.000000",
                    "is_deleted": "최초",
                    "image_url": "http://example.com/image1.jpg",
                    "parent_story": None,
                    "child_stories": ["unique-story-id-002", "unique-story-id-003"]
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-002",
                    "content": "이것은 첫 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T08:00:00.000000",
                    "updated_at": "2024-01-08T08:00:00.000000",
                    "is_deleted": "첫번째",
                    "image_url": "http://example.com/image2.jpg",
                    "parent_story": "unique-story-id-001",
                    "child_stories": ["unique-story-id-004"]
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-003",
                    "content": "이것은 두 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": "두번째",
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-001",
                    "child_stories": ["unique-story-id-005"]
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-004",
                    "content": "이것은 첫 번째의 첫번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": "첫첫번째",
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-002",
                    "child_stories": ["unique-story-id-006","unique-story-id-007"]
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-006",
                    "content": "이것은 첫 번째의 첫 번째의 첫 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": "첫첫첫번째",
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-004",
                    "child_stories": []
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-007",
                    "content": "이것은 첫 번째의 첫 번째의 두 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": "첫첫두번째",
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-004",
                    "child_stories": []
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-005",
                    "content": "이것은 두 번째의 첫 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": "두첫번째",
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-003",
                    "child_stories": []
                }
            }
        ]

    # Neo4j에 데이터 삽입
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        for item in data:
            fields = item['fields']
            if item['model'] == 'user.User':
                session.run(
                    "CREATE (u:User {user_id: $user_id, nickname: $nickname, created_at: datetime($created_at), updated_at: datetime($updated_at), is_deleted: $is_deleted})",
                    user_id=fields['user_id'],
                    nickname=fields['nickname'],
                    created_at=fields['created_at'],
                    updated_at=fields['updated_at'],
                    is_deleted=fields['is_deleted']
                )
            elif item['model'] == 'story.Story':
                session.run(
                    "CREATE (s:Story {story_id: $story_id, content: $content, created_at: datetime($created_at), updated_at: datetime($updated_at), is_deleted: $is_deleted, image_url: $image_url})",
                    story_id=fields['story_id'],
                    content=fields['content'],
                    created_at=fields['created_at'],
                    updated_at=fields['updated_at'],
                    is_deleted=fields['is_deleted'],
                    image_url=fields['image_url']
                )

            # 관계 생성
        for item in data:
            fields = item['fields']
            if item['model'] == 'story.Story':
                # 부모 스토리와의 관계 생성
                # if fields['parent_story']:
                #     session.run(
                #         "MATCH (parent:Story {story_id: $parent_story_id}), (child:Story {story_id: $child_story_id}) CREATE (child)-[:ParentStory]->(parent)",
                #         parent_story_id=fields['parent_story'],
                #         child_story_id=fields['story_id']
                #     )

                # 자식 스토리들과의 관계 생성
                for child_id in fields['child_stories']:
                    session.run(
                        "MATCH (parent:Story {story_id: $parent_story_id}), (child:Story {story_id: $child_story_id}) CREATE (parent)-[:ChildStory]->(child)",
                        parent_story_id=fields['story_id'],
                        child_story_id=child_id
                    )

    driver.close()


if __name__ == "__main__":

     load_data_to_neo4j("init_data.json")
