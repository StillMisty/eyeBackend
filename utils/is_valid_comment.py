# 评论有效性检查函数
import re


def is_valid_comment(comment: str) -> tuple[bool, str]:
    """
    检查评论是否有效
    返回: (是否有效, 无效原因)
    """
    # 去除前后空格
    comment = comment.strip()

    # 检查是否为空或过短
    if not comment:
        return False, "评论内容为空"

    if len(comment) < 3:
        return False, "评论内容太短"

    # 检查重复字符或模式
    # 检测连续重复字符超过3个
    if re.search(r"(.)\1{3,}", comment):
        return False, "包含过多重复字符"

    # 检测同一个词语重复多次
    if re.search(r"(\w{2,})(\s*\1){2,}", comment):
        return False, "包含重复词语"

    # 无意义评论关键词列表
    meaningless_patterns = [
        r"^[.。,，!！?？]+$",  # 只有标点符号
        r"^[呵哈嘿嘻]+$",  # 只有笑声
        r"^666+$",  # 只有666
        r"^[?？]+$",  # 只有问号
        r"^测试",  # 测试开头
        r"^[a-zA-Z0-9]+$",  # 只有单个字母或数字
    ]

    for pattern in meaningless_patterns:
        if re.search(pattern, comment):
            return False, "包含无意义内容"

    # 敏感词检测
    sensitive_words = ["广告", "联系方式", "qq", "微信", "电话"]
    for word in sensitive_words:
        if word in comment.lower():
            return False, "包含敏感词"

    return True, ""
