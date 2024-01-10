import os
import openai
from django.shortcuts import render

# Create your views here.
openai.api_key = os.getenv("GPT_API_KEY")

def generate_image(content): # openai 이용하여 이미지 생성하는 함수

    messages = []
    promptmessages = "이야기를 기반으로 dall-e api 기반으로 그림을 생성하는 서비스야. 내가 이야기를 작성하면 너가 장면이나 인물 묘사를 훨씬 구체적으로 영어로 변경해주고 이야기와 구체적 묘사들을 영어로 바꿔서 출력해줘 \n"
    #키워드는 추가 가능
    prompt_keword = """"Detailed textures", "High resolution", "Dynamic lighting", "Cinematic composition", "Storytelling elements", "Suspenseful atmosphere", "Immersive environment", "Visual storytelling" """

    story_content = promptmessages+content
    messages.append({"role": "user", "content": story_content})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_response = completion['choices'][0]['message']['content'] + prompt_keword

    messages.append({"role": "assistant", "content": assistant_response})

    prompt = assistant_response[0:999] # 프롬프트가 1000자가 최대이므로

    response = openai.Image.create(prompt=prompt, n=1, size="256x256") # gpt에게 받은 프롬프팅을 전달하여 그림생성
    image_url = response["data"][0]["url"]

    return image_url  # 임시로 이미지 url을 리턴하도록 설정

