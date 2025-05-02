from openai import AsyncOpenAI

from Config import Config

if Config.DEEPSEEK_API_KEY is None or Config.DEEPSEEK_API_KEY == "":
    raise ValueError("请在环境变量中设置 DEEPSEEK_API_KEY")

client = AsyncOpenAI(
    api_key=Config.DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"
)


async def get_disease_suggested_from_model(
    disease: str,
    age: int,
    gender: str,
):
    """
    从语言模型中获取对应的疾病建议
    """
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": f"根据患者的性别、年龄和疾病名称，给出该疾病的建议和注意事项。性别：{gender}，年龄：{age}，疾病名称：{disease}",
            },
        ],
        stream=False,
    )

    return response.choices[0].message.content.strip()
