from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf


def preprocess_image(image_path, target_size=(224, 224)):
    """
    读取图像并进行预处理：
      - 读取并转换为RGB
      - 缩放到指定尺寸
      - 归一化到[0, 1]
    返回: shape为 (224, 224, 3) 的numpy数组，取值范围[0,1]
    """
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        raise FileNotFoundError(f"无法读取图像文件: {image_path}")

    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_rgb = cv2.resize(img_rgb, target_size)
    img_rgb = img_rgb.astype(np.float32) / 255.0
    return img_rgb


def get_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    """
    计算指定输入图像的 Grad-CAM 热力图
    参数：
      img_array: 预处理后的图像，形状 (1, H, W, 3)
      model: 已训练的 Sequential 模型，其中第一个层为嵌入的 InceptionV3
      last_conv_layer_name: 目标卷积层名称（例如 'mixed10'）
      pred_index: 可选，指定计算哪个类别的热力图（默认取预测得分最高的类别）
    返回：
      heatmap: 归一化后的热力图，范围 [0,1]
    """
    # 获取嵌入的 InceptionV3 模型
    inception = model.layers[0]

    # 使用 GradientTape 手动构造前向传播
    with tf.GradientTape() as tape:
        # 计算 InceptionV3 部分的输出（即所有卷积特征）
        conv_outputs = inception(img_array)
        tape.watch(conv_outputs)

        # 手动将 conv_outputs 传递给后续层，构造完整的前向传播
        x = conv_outputs
        for layer in model.layers[1:]:
            x = layer(x)
        predictions = x

        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # 计算梯度：目标类别相对于 conv_outputs 的梯度
    grads = tape.gradient(class_channel, conv_outputs)
    if grads is None:
        raise ValueError("梯度计算失败，请检查模型结构和梯度带监控设置。")

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs * pooled_grads
    heatmap = tf.reduce_sum(heatmap, axis=-1)

    # ReLU 截断负值并归一化
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.reduce_max(heatmap)
    if max_val == 0:
        return heatmap.numpy()
    heatmap /= max_val
    return heatmap.numpy()


def generate_gradcam_on_image(img_array, model, last_conv_layer_name, alpha=0.4):
    """
    参数：
      img_array: 形状为 (1, 224, 224, 3) 的预处理图像，归一化到 [0,1]
      model: 已训练的模型
      last_conv_layer_name: 目标卷积层名称，如 'mixed10'
      alpha: 叠加热力图时的透明度
    返回：
      叠加后的 BGR 图像（uint8）
    """
    heatmap = get_gradcam_heatmap(img_array, model, last_conv_layer_name)
    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_resized = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)

    # 原始图像：输入 img_array 的像素范围为 [0,1]，转换为 0-255 的 uint8 格式
    img = np.uint8(img_array[0] * 255)
    superimposed_img = cv2.addWeighted(img, 1 - alpha, heatmap_color, alpha, 0)
    return superimposed_img


def generate_gradcam(
    image_path, model_path=None, last_conv_layer_name="mixed10", alpha=0.4
):
    """
    为给定的图像生成 Grad-CAM 热力图

    参数：
      image_path: 图像文件路径
      model_path: 模型文件路径，如果为None则使用默认路径
      last_conv_layer_name: 目标卷积层名称，默认为'mixed10'
      alpha: 热力图叠加透明度，默认0.4

    返回：
      gradcam_img_bgr: 叠加了热力图的BGR图像
    """
    if model_path is None:
        model_path = Path(__file__).parent / "model.h5"

    # 加载模型
    model = tf.keras.models.load_model(model_path)

    # 预处理图像
    img_rgb = preprocess_image(image_path, target_size=(224, 224))
    img_rgb_expanded = np.expand_dims(img_rgb, axis=0)  # (1,224,224,3)

    # 生成 Grad-CAM 叠加图
    gradcam_img_bgr = generate_gradcam_on_image(
        img_rgb_expanded, model, last_conv_layer_name=last_conv_layer_name, alpha=alpha
    )

    return gradcam_img_bgr


# =========== 使用示例 ===========

if __name__ == "__main__":
    # 1. 指定某张图片的绝对路径
    image_path = (
        r"C:\Users\Still\Downloads\preprocessed_images\preprocessed_images\1_right.jpg"
    )

    # 2. 生成Grad-CAM图像
    gradcam_img_bgr = generate_gradcam(image_path)

    # 3. 加载原始图像进行对比展示
    img_rgb = preprocess_image(image_path, target_size=(224, 224))

    # 4. 可视化：左边原图，右边 Grad-CAM
    plt.figure(figsize=(10, 5))

    # 左：原图
    plt.subplot(1, 2, 1)
    plt.imshow(img_rgb)  # img_rgb 取值范围[0,1]
    plt.title("Original Image")
    plt.axis("off")

    # 右：Grad-CAM
    gradcam_img_rgb = cv2.cvtColor(gradcam_img_bgr, cv2.COLOR_BGR2RGB)
    plt.subplot(1, 2, 2)
    plt.imshow(gradcam_img_rgb)
    plt.title("Grad-CAM")
    plt.axis("off")

    plt.tight_layout()
    plt.show()
