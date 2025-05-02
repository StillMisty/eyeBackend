from openai import AsyncOpenAI

from Config import Config

disease2details = {
    "branch retinal vein occlusion": {
        "chinese_name": "视网膜分支静脉阻塞",
        "details": "视网膜分支静脉被堵塞，导致该分支供血区域的视网膜缺血、出血和水肿，影响部分视野和视力。",
    },
    "cataract": {
        "chinese_name": "白内障",
        "details": "眼睛的晶状体发生混浊，阻碍光线通过，导致视力下降。通常与年龄相关，是主要的致盲原因之一。",
    },
    "central retinal vein occlusion": {
        "chinese_name": "视网膜中央静脉阻塞",
        "details": "视网膜中央静脉被堵塞，导致整个视网膜静脉回流受阻，出现广泛出血和水肿，严重影响视力。",
    },
    "chorioretinal atrophy": {
        "chinese_name": "脉络膜视网膜萎缩",
        "details": "脉络膜和视网膜组织同时发生的变薄和退化，常表现为眼底色素紊乱和脉络膜血管显露，可由多种原因引起。",
    },
    "diabetic retinopathy": {
        "chinese_name": "糖尿病性视网膜病变",
        "details": "糖尿病导致的视网膜血管损伤性病变，是糖尿病的主要微血管并发症之一，严重时可致盲。包括非增殖期和增殖期。",
    },
    "drusen": {
        "chinese_name": "玻璃膜疣",
        "details": "位于视网膜色素上皮层与Bruch膜之间的黄色沉积物，常见于年龄相关性黄斑变性早期，多数小的玻璃膜疣无症状。",
    },
    "dry age-related macular degeneration": {
        "chinese_name": "干性年龄相关性黄斑变性",
        "details": "年龄相关性黄斑变性中最常见的类型，以玻璃膜疣和视网膜色素上皮萎缩为特征，进展缓慢，通常视力下降较轻。",
    },
    "epiretinal membrane": {
        "chinese_name": "视网膜前膜",
        "details": "在视网膜内表面形成的一层纤维膜，可牵拉视网膜导致视物变形、扭曲或视力下降。根据位置可进一步细分。",
    },
    "epiretinal membrane over the macula": {
        "chinese_name": "黄斑前膜",
        "details": "特指位于视网膜黄斑区域的视网膜前膜，由于影响视力最敏锐的区域，常导致中心视力明显下降和变形。",
    },
    "glaucoma": {
        "chinese_name": "青光眼",
        "details": "一组导致视神经进行性损伤的疾病，通常与眼内压升高有关，视神经损伤会导致视野缺损，是主要致盲眼病之一。",
    },
    "hypertensive retinopathy": {
        "chinese_name": "高血压性视网膜病变",
        "details": "长期或急剧高血压引起的视网膜血管和组织损伤，表现为血管狭窄、硬化、出血、渗出或视盘水肿。",
    },
    "laser spot": {
        "chinese_name": "激光斑",
        "details": "眼底激光治疗后在视网膜上留下的局限性瘢痕，通常呈圆形或椭圆形色素沉着。",
    },
    "lens dust": {
        "chinese_name": "镜片灰尘/污垢",
        "details": "并非眼部疾病，是指检查设备（如眼底镜、裂隙灯）的镜片上的灰尘、污迹或划痕，影响眼底图像质量。",
    },
    "macular epiretinal membrane": {
        "chinese_name": "黄斑部视网膜前膜",
        "details": "与“黄斑前膜”同义，指位于视网膜黄斑区域表面的纤维膜，会影响中心视力。",
    },
    "maculopathy": {
        "chinese_name": "黄斑病变",
        "details": "泛指各种累及视网膜黄斑区域的疾病，黄斑是负责中心视力和精细视觉的区域，黄斑病变常导致中心视力下降。",
    },
    "mild nonproliferative retinopathy": {
        "chinese_name": "轻度非增殖性视网膜病变",
        "details": "糖尿病性视网膜病变的早期阶段，眼底表现为微动脉瘤和少量点状出血，视力通常不受影响。",
    },
    "moderate non proliferative retinopathy": {
        "chinese_name": "中度非增殖性视网膜病变",
        "details": "糖尿病性视网膜病变的一个阶段，眼底表现为较多的微动脉瘤、出血和硬性渗出，视力可能受黄斑水肿影响。",
    },
    "myelinated nerve fibers": {
        "chinese_name": "有髓神经纤维",
        "details": "视网膜神经纤维层中髓鞘发育异常，表现为从视盘向外延伸的白色、边界模糊的羽毛状区域。通常为先天性良性改变。",
    },
    "myopia retinopathy": {
        "chinese_name": "近视性视网膜病变",
        "details": "高度近视引起的视网膜和脉络膜病变，包括视网膜变薄、格子样变性、裂孔、脉络膜新生血管等，增加了视网膜脱离等风险。",
    },
    "normal fundus": {
        "chinese_name": "正常眼底",
        "details": "眼科检查显示视网膜、视盘、视网膜血管和脉络膜等眼底结构形态、颜色正常，无病理改变。",
    },
    "optic disc edema": {
        "chinese_name": "视盘水肿",
        "details": "视神经盘（视神经在眼球内的起始部分）因液体积聚而肿胀隆起，可能是多种疾病的征象，包括颅内压增高。",
    },
    "pathological myopia": {
        "chinese_name": "病理性近视",
        "details": "指近视度数高（通常高于-6.00D）且眼轴进行性拉长，导致眼球后段发生一系列退行性病变，如视网膜萎缩、裂孔、黄斑出血等，视力损伤风险高。",
    },
    "peripapillary atrophy": {
        "chinese_name": "视盘周围萎缩",
        "details": "视神经盘周围视网膜色素上皮和脉络膜组织的萎缩区域，常见于高度近视、青光眼或老年人。",
    },
    "post laser photocoagulation": {
        "chinese_name": "激光光凝术后",
        "details": "指眼底曾接受过激光光凝治疗，眼底可见激光治疗留下的色素性瘢痕，用于治疗糖尿病性视网膜病变、视网膜裂孔等。",
    },
    "post retinal laser surgery": {
        "chinese_name": "视网膜激光手术后",
        "details": "与“激光光凝术后”含义相似，指示视网膜因病变接受了激光治疗，眼底可见相应的激光斑。",
    },
    "proliferative diabetic retinopathy": {
        "chinese_name": "增殖性糖尿病性视网膜病变",
        "details": "糖尿病性视网膜病变的晚期阶段，视网膜或视盘上出现异常新生血管，这些新生血管脆弱易破裂出血，可引起玻璃体出血和牵拉性视网膜脱离。",
    },
    "refractive media opacity": {
        "chinese_name": "屈光介质混浊",
        "details": "指光线进入眼内通过的屈光介质（角膜、房水、晶状体、玻璃体）出现混浊，导致视物不清，如角膜混浊、白内障、玻璃体混浊等。",
    },
    "retinal pigmentation": {
        "chinese_name": "视网膜色素沉着",
        "details": "指视网膜色素上皮细胞色素的异常积累或分布，表现为眼底色素斑点或线条，可见于多种视网膜病变或为生理变异。",
    },
    "retinitis pigmentosa": {
        "chinese_name": "视网膜色素变性",
        "details": "一组遗传性视网膜疾病，主要表现为视网膜感光细胞和色素上皮的进行性退化，典型症状为夜盲、视野进行性缩小，眼底可见骨细胞样色素沉着。",
    },
    "severe nonproliferative retinopathy": {
        "chinese_name": "重度非增殖性视网膜病变",
        "details": "糖尿病性视网膜病变的一个晚期非增殖阶段，眼底出血、微动脉瘤、硬性渗出等病变广泛且严重，视网膜可能出现血管异常（IRMA），有向增殖期进展的高风险。",
    },
    "severe proliferative diabetic retinopathy": {
        "chinese_name": "严重增殖性糖尿病性视网膜病变",
        "details": "增殖性糖尿病性视网膜病变的更严重阶段，新生血管广泛且数量多，常伴有玻璃体出血、纤维膜增生和牵拉性视网膜脱离风险。",
    },
    "spotted membranous change": {
        "chinese_name": "点状膜样变性",
        "details": "眼底出现的点状或斑片状膜样改变，形态和病因多样，需要结合临床具体分析。",
    },
    "suspected glaucoma": {
        "chinese_name": "可疑青光眼",
        "details": "存在可能提示青光眼的迹象（如眼压偏高、视盘C/D比异常、视野轻微缺损等），但尚未达到明确诊断青光眼的标准，需进一步随访或检查。",
    },
    "tessellated fundus": {
        "chinese_name": "豹纹状眼底",
        "details": "由于视网膜色素上皮层色素较少或变薄，使得脉络膜血管纹理更清晰显露，眼底呈网格状或类似豹纹的外观。多见于生理性变异或高度近视。",
    },
    "vitreous degeneration": {
        "chinese_name": "玻璃体变性",
        "details": "玻璃体（填充眼球后部的胶状物质）发生液化、混浊或后脱离，表现为飞蚊症（眼前有漂浮物）或闪光感。",
    },
    "wet age-related macular degeneration": {
        "chinese_name": "湿性年龄相关性黄斑变性",
        "details": "年龄相关性黄斑变性的类型之一，以黄斑区域异常新生血管形成并渗漏、出血为特征，进展迅速，常导致中心视力急剧下降。",
    },
    "white vessel": {
        "chinese_name": "白线样血管",
        "details": "视网膜血管壁因炎症、硬化、纤维化等原因增厚或被鞘膜包绕，使血管外观失去正常的红色血柱而呈白色或灰白色。",
    },
}


def get_details_by_disease_name(disease_name: str):
    """
    根据疾病名称获取疾病详情
    """
    return disease2details.get(disease_name, None)


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
