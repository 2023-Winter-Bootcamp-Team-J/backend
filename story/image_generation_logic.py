#비동기 처리를 위한 이미지 생성 함수 분리
import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image_logic(content):
    try:
        prompt_keyword = "American Cartoon drawing style, High-quality image"

        response = openai.Image.create(
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            # prompt="다음 이야기를 소설의 한장면의 그림같이 만들어줘 일러스트같이 만들어줘. 이미지 안에 어떠한 텍스트나 라벨도 포함되지 않는, 순수한 시각적 예술 작품을 원합니다. 배경 설명, 문자, 라벨을 포함하지 말아주세요. 오직 요청한 시나리오에 근거한 이미지만을 생성해 주세요. 말풍선이나 대사 없이 조용한 순간을 표현해 주세요. \n  "+content+ " \n 중요한 특징은 절대 빼먹지마, 장소, 인물, 특징, 시간대, 기분, 행동, 풍경 모두 담을 수 있도록 해.  + Please don't put the letters in the image. \n Please do not include any text or label in the picture.\n 대사 넣지 마 without letter" + prompt_keyword,
#             prompt ="""
# 이미지를 생성할 때, 다음 조건을 꼭 지켜주세요: 이미지 내에 어떠한 텍스트도 포함되지 않아야 합니다. 캐릭터의 대화나 생각을 나타내는 말풍선이나 글자는 넣지 말아 주세요. 순수하게 시각적인 요소만으로 이야기의 한 장면을 표현해주세요\n
# 단순하고 명확한 하나의 장면을 포함한 이미지를 생성해 주세요. 복잡한 부연 설명, 텍스트 박스, 또는 다른 장면들이 없는, 주인공이 활동하는 단일 장면에 초점을 맞춘 이미지를 원합니다."
#
#             """+ content + prompt_keyword,
            prompt = """
            "Please ensure the following conditions when generating the image: The image must not include any text. Do not add speech bubbles or text that represents the character's dialogue or thoughts. The image should purely represent a scene with visual elements only. 
Create an image that contains a simple and clear single scene. Focus on the protagonist in action without complicated supplementary explanations, text boxes, or additional scenes."
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