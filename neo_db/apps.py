from django.apps import AppConfig
from neo4j import GraphDatabase

class NeoDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'neo_db'

    def ready(self):
        self.import_data_to_neo4j()

    def import_data_to_neo4j(self):
        # Neo4j 데이터베이스 연결 설정
        uri = "bolt://localhost:7474"
        user = "neo4j"  # 사용자 이름
        password = "nextpage"  # 비밀번호
        driver = GraphDatabase.driver(uri, auth=(user, password))

        # 데이터 정의
        data = [
            # 사용자 데이터
            {
                "model": "user.User",
                "fields": {
                    "user_id": "unique-user-id-001",
                    "nickname": "Kanguk",
                    "created_at": "2024-01-08T06:39:55.329190",
                    "updated_at": "2024-01-08T06:39:55.329261",
                    "is_deleted": False
                }
            },
            # 스토리 데이터
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-001",
                    "content": "이것은 최초의 스토리 내용입니다.",
                    "created_at": "2024-01-08T07:00:00.000000",
                    "updated_at": "2024-01-08T07:00:00.000000",
                    "is_deleted": False,
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
                    "is_deleted": False,
                    "image_url": "http://example.com/image2.jpg",
                    "parent_story": "unique-story-id-001",
                    "child_stories": []
                }
            },
            {
                "model": "story.Story",
                "fields": {
                    "story_id": "unique-story-id-003",
                    "content": "이것은 두 번째 분기 스토리 내용입니다.",
                    "created_at": "2024-01-08T09:00:00.000000",
                    "updated_at": "2024-01-08T09:00:00.000000",
                    "is_deleted": False,
                    "image_url": "http://example.com/image3.jpg",
                    "parent_story": "unique-story-id-001",
                    "child_stories": []
                }
            }
        ]

        # Neo4j 데이터베이스에 데이터 삽입
        with driver.session() as session:
            for item in data:
                if item['model'] == 'user.User':
                    self.create_user(session, item['fields'])
                elif item['model'] == 'story.Story':
                    self.create_story(session, item['fields'])

        driver.close()

    def create_user(self, session, fields):
        # 사용자 노드 생성 쿼리
        query = """
        CREATE (u:User {user_id: $user_id, nickname: $nickname, created_at: $created_at, updated_at: $updated_at, is_deleted: $is_deleted})
        """
        session.run(query, parameters=fields)

    def create_story(self, session, fields):
        # 스토리 노드 생성 쿼리
        create_story_query = """
        CREATE (s:Story {story_id: $story_id, content: $content, created_at: $created_at, updated_at: $updated_at, is_deleted: $is_deleted, image_url: $image_url})
        """
        session.run(create_story_query, parameters=fields)

        # 스토리 간의 관계 설정 쿼리
        for child_id in fields.get("child_stories", []):
            self.create_story_relationship(session, fields["story_id"], child_id)

    def create_story_relationship(self, session, parent_id, child_id):
        # 부모 스토리와 자식 스토리 간의 관계 생성 쿼리
        query = """
        MATCH (parent:Story {story_id: $parent_id}), (child:Story {story_id: $child_id})
        MERGE (parent)-[:HAS_CHILD]->(child)
        """
        session.run(query, parameters={"parent_id": parent_id, "child_id": child_id})