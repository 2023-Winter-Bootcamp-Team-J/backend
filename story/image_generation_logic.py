#비동기 처리를 위한 이미지 생성 함수 분리
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image_logic(content):
    try:
        prompt_keyword = """Design: a detailed digital illustration drawn with bright colors and clean lines. Please make the following images according to the previous requirements: """

        response = openai.Image.create(
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            prompt="""
                When generating an image, be sure to observe the following conditions: Do not add text to the image. 
                I want an illustration image, not contain text in the image.
                """ + prompt_keyword + content,
            n=1
        )

        image_url = response.data[0].url
        return {
            'message': '이미지가 생성되었습니다.',
            'image_url': image_url,
        }
    except openai.error.InvalidRequestError as e: #부적절 내용 예외처리
        return {"error": "Invalid content. Please check your content."}
        # return Response(error_message, status=status.HTTP_400_BAD_REQUEST)