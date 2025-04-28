import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # 只显示 Error 信息

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import tensorflow as tf

model_path = Path(__file__).parent / "model.h5"

# 创建线程池执行器
_thread_pool = ThreadPoolExecutor()

# ========== 1. 加载训练好的模型 ==========
model = tf.keras.models.load_model(model_path, compile=False)

# ========== 2. 定义类别名称 ==========
label_names = [
    "branch retinal vein occlusion",  # O
    "cataract",  # C
    "central retinal vein occlusion",  # O
    "chorioretinal atrophy",  # O
    "diabetic retinopathy",  # D
    "drusen",  # O
    "dry age-related macular degeneration",  # A
    "epiretinal membrane",  # O
    "epiretinal membrane over the macula",  # O
    "glaucoma",  # G
    "hypertensive retinopathy",  # H
    "laser spot",  # O
    "lens dust",  # None
    "macular epiretinal membrane",  # O
    "maculopathy",  # O
    "mild nonproliferative retinopathy",  # D
    "moderate non proliferative retinopathy",  # D
    "myelinated nerve fibers",  # O
    "myopia retinopathy",  # M
    "normal fundus",  # N
    "optic disc edema",  # O
    "pathological myopia",  # M
    "peripapillary atrophy",  # O
    "post laser photocoagulation",  # O
    "post retinal laser surgery",  # O
    "proliferative diabetic retinopathy",  # D
    "refractive media opacity",  # O
    "retinal pigmentation",  # O
    "retinitis pigmentosa",  # O
    "severe nonproliferative retinopathy",  # D
    "severe proliferative diabetic retinopathy",  # D
    "spotted membranous change",  # O
    "suspected glaucoma",  # G
    "tessellated fundus",  # O
    "vitreous degeneration",  # O
    "wet age-related macular degeneration",  # A
    "white vessel",  # O
]

# ========== 2.1 标签类别字典 ==========
label_categories = [
    "O",
    "C",
    "O",
    "O",
    "D",
    "O",
    "A",
    "O",
    "O",
    "G",
    "H",
    "O",
    None,
    "O",
    "O",
    "D",
    "D",
    "O",
    "M",
    "N",
    "O",
    "M",
    "O",
    "O",
    "O",
    "D",
    "O",
    "O",
    "O",
    "D",
    "D",
    "O",
    "G",
    "O",
    "O",
    "A",
    "O",
]

# 将标签名和对应的类别映射成字典
label_to_category = {name: cat for name, cat in zip(label_names, label_categories)}


# ========== 3. 定义图像预处理函数 ==========
def load_and_preprocess_image(image_path, target_size=224):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"图像无法读取: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (target_size, target_size))
    image = image.astype("float32") / 255.0
    image = np.expand_dims(image, axis=0)
    return image


# ========== 4. 预测单张图像的多标签结果 ==========
def predict_single_image(image_path):
    preprocessed = load_and_preprocess_image(image_path)
    preds = model.predict(preprocessed)
    predicted_mask = preds[0]

    label_with_category = []

    for i, val in enumerate(predicted_mask):
        label = label_names[i]
        label_with_category.append(
            {
                "label": label,
                "probability": val.item(),
            }
        )

    return label_with_category


def identify_eye(image_path: Path, threshold: float = 0.1) -> tuple:
    """识别眼部疾病

    Args:
        image_path (Path): 图像文件路径
        threshold (float, optional): 置信值. Defaults to 0.1.

    Returns:
        predicted_categories_list: 预测的疾病种类列表
    """
    label_with_category = predict_single_image(image_path)
    filtered_results = [
        item for item in label_with_category if item["probability"] >= threshold
    ]

    # 如果过滤后的结果为空，则至少保留一个概率最高的结果
    if not filtered_results:
        # 找出概率最高的一个结果
        max_prob_item = max(label_with_category, key=lambda x: x["probability"])
        filtered_results = [max_prob_item]

    return sorted(filtered_results, key=lambda x: x["probability"], reverse=True)


async def identify_eye_async(image_path: Path, threshold: float = 0.1) -> tuple:
    """异步识别眼部疾病

    Args:
        image_path (Path): 图像文件路径
        threshold (float, optional): 置信值. Defaults to 0.1.

    Returns:
        predicted_categories_list: 预测的疾病种类列表
    """
    # 在线程池中运行CPU密集型任务，避免阻塞事件循环
    return await asyncio.get_event_loop().run_in_executor(
        _thread_pool, identify_eye, image_path, threshold
    )
