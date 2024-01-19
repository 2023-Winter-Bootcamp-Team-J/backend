#비동기 처리를 위한 이미지 생성 함수 분리
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image_logic(content):
    try:
        prompt_keyword = "미국 카툰 그림체, High-quality image"

        response = openai.Image.create(
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            prompt="다음 이야기를 소설의 한장면의 그림같이 만들어줘 일러스트같이 만들어줘. 이미지 안에 어떠한 텍스트나 라벨도 포함되지 않는, 순수한 시각적 예술 작품을 원합니다. 배경 설명, 문자, 라벨을 포함하지 말아주세요. 오직 요청한 시나리오에 근거한 이미지만을 생성해 주세요.  "+content+ " 중요한 특징은 절대 빼먹지마, 장소, 인물, 특징, 시간대, 기분, 행동, 풍경 모두 담을 수 있도록 해. " + prompt_keyword + "Please don't put the letters in the image. \n Please do not include any text or label in the picture.\n 대사 넣지 마 without letter" ,
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