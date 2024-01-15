#비동기 처리를 위한 이미지 생성 함수 분리
import os

import openai
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import status

load_dotenv()  # 이 부분이 .env 파일을 로드합니다.
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image_logic(content):
    messages = []
    promptmessages = """
    우리는 지금 스토리를 작성하면 이미지를 생성해주는 서비스를 진행중이야
    dalle-api를 사용하여 이미지를 생성하는데, 이미지 요청문을 gpt api를 이용하여 생성하고 , 그 요청문을 dalle에게 전달하는 형식으로 진행중이야.

    내가 원하는 형식은 우리가 스토리를 작성하면 이야기 속에서 핵심 키워드 (인물, 장소, 사물, 분위기, 배경 등) 를 파악하여 뒤에 키워드로 붙여줘(예시 형태: charactor: Jone, place: school) 
    이 출력값은 그림 생성 요청문으로 쓰일거니까 그림 생성에 적절한 핵심 키워드들을 출력해줘야해 
    그리고 키워드들을 토대로 그림 생성 요청문을 작성해. 그 요청문을 출력하도록 해
    출력값은 영어로 출력하도록 해

    story: 

    이제 내가 이야기를 입력할거야 바로 내가 원하는 결과값만 출력하도록 해 앞 뒤 설명 필요없이 그림 생성 요청문만 출력하면 돼 story: 
    """
    # 키워드는 추가 가능
    prompt_keword = """ \n image_characteristic: "High-Definition" ,"Epic Landscape", "Clear Outlines" , "Fantasy" or "Adventure" ,"High Level of Detail", ""An old, enchanted mansion interior in the style of a classic Disney animation. The image should have vibrant colors and a magical atmosphere, with exaggerated and whimsical design elements that give it a fairy tale-like quality. There should be intricate details and a sense of wonder, akin to the settings often found in animated musical adventures." """
    # """"Detailed textures", "High resolution", "Dynamic lighting", "Cinematic composition", "Storytelling elements", "Suspenseful atmosphere", "Immersive environment", "Visual storytelling","Sophisticated Style", "Modern Feel","realistic", "fine work",  """

    story_content = promptmessages + content
    messages.append({"role": "user", "content": story_content})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_response = completion['choices'][0]['message']['content'] + prompt_keword

    messages.append({"role": "assistant", "content": assistant_response})

    prompt = assistant_response[0:999]  # 프롬프트가 1000자가 최대이므로

    response = openai.Image.create(prompt=prompt, n=1, size="256x256")  # gpt에게 받은 프롬프팅을 전달하여 그림생성
    image_url = response["data"][0]["url"]

    return {
        'message': '이미지가 생성되었습니다.',
        'image_url': image_url,
    }