from celery import shared_task
from .image_generation_logic import generate_image_logic

@shared_task
def generate_image_async(content):
    return generate_image_logic(content) # 비동기 처리 대상인 기존 함수 호출