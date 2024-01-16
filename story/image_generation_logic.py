#비동기 처리
# 를 위한 이미지 생성 함수 분리
import os
import openai

from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import status
load_dotenv()  # 이 부분이 .env 파일을 로드합니다.
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image_logic(content):
    try:
        #gpt 부분 임시로 빼봄

        # messages = []
        # promptmessages = """
        # 우리는 지금 스토리를 작성하면 이미지를 생성해주는 서비스를 진행중이야
        # dalle-api를 사용하여 이미지를 생성하는데, 이미지 요청문을 gpt api를 이용하여 생성하고 , 그 요청문을 dall-e에게 전달하는 형식으로 진행중이야.
        #
        # 이야기를 입력받으면, 그 이야기에서 핵심 키워드를 너가 뽑아. 키워드는 이야기 내 등장하는 인물, 장소, 장소의 특징, 색감, 분위기, 시간대, 기분 등을 파악하여 키워드로 정리를 해서 키워드로 출력해줘
        # 예시를 들면 "샘은 신비한 숲의 입구에 서 있습니다. 숲은 두 개의 서로 다른 경로로 나뉘어져 있으며, 각각은 전혀 다른 모험을 약속합니다." 이런 스토리를 입력 받으면
        # 너는 다음과 같이 출력하면 돼
        # "인물: 샘, 장소: 두 갈래 숲, 분위기: 신비함, 기분: 모험적"
        # 이렇게 출력해 주면돼 이 예시는 절대 출력하지말고 너의 출력 예시로 쓰도록 해
        #
        # 정리하자면, 이야기를 입력받으면 그 이야기의 핵심 키워드를 출력하면 돼 출력값은 키워드만 바로 출력해 앞 뒤 설명, 붙임말같은것은 출력하지마
        #
        # 이제 내가 이야기를 입력할거야 바로 내가 원하는 결과값만 출력하도록 해 앞 뒤 설명 필요없이 그림 생성 요청문만 출력하면 돼 story:
        # """
        # # 키워드는 추가 가능
        # prompt_keword = "수채화,  "
        # story_content = promptmessages + content
        # messages.append({"role": "user", "content": story_content})
        #
        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages
        # )
        # assistant_response = completion['choices'][0]['message']['content'] + prompt_keword
        #
        # messages.append({"role": "assistant", "content": assistant_response})
        #
        # prompt = assistant_response[0:999]  # 프롬프트가 1000자가 최대이므로

        # response = openai.Image.create(prompt=prompt, n=1, size="256x256")  # gpt에게 받은 프롬프팅을 전달하여 그림생성
        # image_url = response["data"][0]["url"]
        prompt_keyword = "수채화풍, High-quality image"

        response = openai.Image.create(
            model="dall-e-3",
            size="1024x1024",
            quality="standard",
            prompt="다음 이야기를 소설의 한장면의 그림같이 만들어줘 일러스트같이 만들어줘.  "+content+ " 중요한 특징은 절대 빼먹지마, 장소, 인물, 특징, 시간대, 기분, 행동, 풍경 모두 담을 수 있도록 해. " + prompt_keyword + "Please don't put the letters in the image when you create the image" ,
            n=1
        )

        image_url = response.data[0].url
        return {
            'message': '이미지가 생성되었습니다.',
            'image_url': image_url,
        }
    except openai.error.InvalidRequestError as e: #부적절 내용 예외처리
        error_message = {"error": "Invalid content. Please check your content."}
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)