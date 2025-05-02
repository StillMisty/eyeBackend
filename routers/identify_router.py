import json
import os
import shutil
import uuid
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Optional

import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.auth_handler import get_current_user
from Config import Config
from database import get_db
from entity.Order import Order
from eye_identify import generate_gradcam, identify_eye_async
from models.EyeIdentification import EyeIdentification
from models.IdentifySuggestions import IdentifySuggestions
from models.Users import Gender, Users
from utils import get_details_by_disease_name, get_disease_suggested_from_model

router = APIRouter(
    prefix="/identify",
    tags=["眼疾识别"],
    responses={404: {"description": "Not found"}},
)

# 保存上传图像的目录
UPLOAD_DIR = Config.get_upload_dir()
# 确保目录存在
UPLOAD_DIR.mkdir(exist_ok=True)


class EyeIdentificationDetail(BaseModel):
    chinese_name: str
    details: str


class EyeIdentificationResult(BaseModel):
    """
    眼部识别记录详情的Pydantic模型
    """

    label: str
    probability: float
    details: EyeIdentificationDetail


class EyeIdentificationResponse(BaseModel):
    """
    创建眼部识别记录的Pydantic模型
    """

    id: int
    results: list[EyeIdentificationResult]
    image_url: str
    created_at: datetime


class EyeIdentificationSuggestion(BaseModel):
    """
    眼部疾病建议的Pydantic模型
    """

    id: int
    age: int
    gender: Gender
    disease: str
    suggestion: str
    created_at: datetime


@router.post(
    "/eye",
    summary="眼部疾病识别",
    response_model=EyeIdentificationResponse,
)
async def identify_eye_disease(
    file: UploadFile = File(...),
    threshold: float = Config.IDENTIFICATION_CONFIG["default_threshold"],
    db: Session = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user),
):
    """
    眼部疾病识别接口

    - **file**: 上传的眼部图像文件
    - **threshold**: 识别阈值（可选，默认0.1）
    """
    # 验证文件类型
    allowed_types = Config.get_allowed_types()
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持{', '.join([t.split('/')[-1].upper() for t in allowed_types])}格式的图像",
        )

    try:
        # 创建临时文件
        with NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件内容复制到临时文件
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # 使用异步函数进行识别，不会阻塞事件循环
        results = await identify_eye_async(temp_file_path, threshold)
        for result in results:
            if "label" in result:
                result["details"] = get_details_by_disease_name(result["label"])

        # 创建存储目录（按年月日组织）
        today = datetime.now()
        save_dir = UPLOAD_DIR / str(today.year) / str(today.month) / str(today.day)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1]
        unique_filename = (
            f"{today.strftime('%H%M%S')}_{uuid.uuid4().hex[:8]}{extension}"
        )
        save_path = save_dir / unique_filename

        # 将临时文件移动到目标位置
        shutil.move(temp_file_path, save_path)

        # 保存识别记录到数据库
        eye_identification = EyeIdentification(
            user_id=current_user.id if current_user else None,
            image_path=str(save_path),
            results=json.dumps(results),
        )
        db.add(eye_identification)
        db.commit()
        db.refresh(eye_identification)

        # 构建图片访问URL
        image_url = f"/api/v1/identify/images/{eye_identification.id}"
        # 获取疾病详细描述
        return {
            "id": eye_identification.id,
            "results": results,
            "image_url": image_url,
            "created_at": eye_identification.created_at.isoformat(),
        }

    except Exception as e:
        # 清理临时文件
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"识别过程中发生错误: {str(e)}",
        )


@router.get("/images/{identification_id}", summary="获取眼部图像")
async def get_eye_image(
    identification_id: int,
    db: Session = Depends(get_db),
):
    """
    获取特定识别记录的眼部图像。只有图像所有者可以访问。

    - **identification_id**: 识别记录ID
    """
    # 查询特定的识别记录
    record = (
        db.query(EyeIdentification)
        .filter(EyeIdentification.id == identification_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="识别记录不存在",
        )

    # 获取图像路径并返回文件
    image_path = record.image_path
    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="图像文件不存在",
        )

    return FileResponse(image_path)


@router.get("/history", summary="获取眼部识别历史记录")
async def get_identification_history(
    skip: int = 0,
    limit: int = 10,
    sort: str = "created_at",
    order: Order = Order.DESC,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    获取当前用户的眼部识别历史记录

    - **skip**: 跳过的记录数（分页用）
    - **limit**: 返回的最大记录数（分页用）
    """
    # 查询当前用户的识别历史
    query = db.query(EyeIdentification).filter(
        EyeIdentification.user_id == current_user.id
    )

    # 动态排序
    if hasattr(EyeIdentification, sort):
        order_column = getattr(EyeIdentification, sort)
        if order == Order.DESC:
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())
    else:
        # 如果提供了无效的排序字段，则使用默认排序（创建时间降序）
        query = query.order_by(EyeIdentification.created_at.desc())

    # 分页
    history = query.offset(skip).limit(limit).all()

    # 统计总记录数
    total_count = (
        db.query(EyeIdentification)
        .filter(EyeIdentification.user_id == current_user.id)
        .count()
    )

    # 转换为字典列表并添加图片URL
    results = []
    for record in history:
        results.append(
            {
                "id": record.id,
                "results": json.loads(record.results),
                "created_at": record.created_at.isoformat(),
                "image_url": f"/api/v1/identify/images/{record.id}",
            }
        )

    return {
        "total": total_count,
        "items": results,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total_count + limit - 1) // limit if limit > 0 else 1,
    }


@router.get(
    "/history/{identification_id}",
    summary="获取特定识别记录详情",
    response_model=EyeIdentificationResponse,
)
async def get_identification_detail(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    获取特定识别记录的详细信息

    - **identification_id**: 识别记录ID
    """
    # 查询特定的识别记录
    record = (
        db.query(EyeIdentification)
        .filter(
            EyeIdentification.id == identification_id,
            EyeIdentification.user_id == current_user.id,
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="识别记录不存在或无权访问",
        )

    record_dict = record.to_dict()
    # 添加图片访问URL
    record_dict["image_url"] = f"/api/v1/identify/images/{record.id}"
    return record_dict


@router.post(
    "/suggestion",
    summary="获取眼部疾病建议",
    response_model=EyeIdentificationSuggestion,
)
async def get_disease_suggestion(
    disease: str,
    age: int,
    gender: Gender,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    获取眼部疾病建议

    - **disease**: 疾病名称
    - **age**: 用户年龄
    - **gender**: 用户性别
    """
    # 验证是否已经存在相同记录
    record = (
        db.query(IdentifySuggestions)
        .filter(
            IdentifySuggestions.disease == disease,
            IdentifySuggestions.age == age,
            IdentifySuggestions.gender == gender,
        )
        .first()
    )

    # 如果记录已存在，返回现有记录
    if record:
        return record.to_dict()

    # 创建新的识别建议记录
    suggestion = await get_disease_suggested_from_model(disease, age, gender)

    # 保存识别建议记录到数据库
    db_suggestion = IdentifySuggestions(
        age=age,
        gender=gender,
        disease=disease,
        suggestion=suggestion,
    )

    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion.to_dict()


@router.delete(
    "/history/{identification_id}",
    summary="删除识别记录",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_identification_record(
    identification_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """
    删除特定的识别记录

    - **identification_id**: 识别记录ID
    """
    # 查询特定的识别记录
    record = (
        db.query(EyeIdentification)
        .filter(
            EyeIdentification.id == identification_id,
            EyeIdentification.user_id == current_user.id,
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="识别记录不存在或无权访问",
        )

    # 删除记录
    db.delete(record)
    db.commit()

    # 删除图像文件
    if os.path.exists(record.image_path):
        os.remove(record.image_path)


@router.post(
    "/gradcam",
    summary="生成眼部图像的Grad-CAM热力图",
    response_description="返回叠加了热力图的JPEG图像",
)
async def create_gradcam(
    file: UploadFile = File(...),
    alpha: float = 0.4,
    last_conv_layer_name: str = "mixed10",
    db: Session = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user),
):
    """
    为上传的眼部图像生成Grad-CAM热力图，展示模型关注的区域

    - **file**: 上传的眼部图像文件
    - **alpha**: 热力图透明度，值范围0-1，默认0.4
    - **last_conv_layer_name**: 目标卷积层名称，默认为'mixed10'
    """
    # 验证文件类型
    allowed_types = Config.get_allowed_types()
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持{', '.join([t.split('/')[-1].upper() for t in allowed_types])}格式的图像",
        )

    # 参数验证
    if not (0 <= alpha <= 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="alpha参数必须在0到1之间",
        )

    try:
        # 创建临时文件
        with NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件内容复制到临时文件
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # 使用generate_gradcam函数生成热力图
        gradcam_img_bgr = generate_gradcam(
            image_path=temp_file_path,
            model_path=None,  # 使用默认模型
            last_conv_layer_name=last_conv_layer_name,
            alpha=alpha,
        )

        # 将OpenCV格式的图像（BGR）编码为JPEG格式
        _, img_encoded = cv2.imencode(".jpg", gradcam_img_bgr)

        # 删除临时文件
        os.unlink(temp_file_path)

        # 返回图像数据
        return Response(content=img_encoded.tobytes(), media_type="image/jpeg")

    except Exception as e:
        # 清理临时文件
        if "temp_file_path" in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Grad-CAM过程中发生错误: {str(e)}",
        )


@router.post(
    "/gradcam/{identification_id}",
    summary="为已存在的识别记录生成Grad-CAM热力图",
    response_description="返回叠加了热力图的JPEG图像",
)
async def create_gradcam_for_record(
    identification_id: int,
    alpha: float = 0.4,
    last_conv_layer_name: str = "mixed10",
    db: Session = Depends(get_db),
    current_user: Optional[Users] = Depends(get_current_user),
):
    """
    为已存在的识别记录生成Grad-CAM热力图

    - **identification_id**: 识别记录ID
    - **alpha**: 热力图透明度，值范围0-1，默认0.4
    - **last_conv_layer_name**: 目标卷积层名称，默认为'mixed10'
    """
    # 参数验证
    if not (0 <= alpha <= 1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="alpha参数必须在0到1之间",
        )

    # 查询特定的识别记录
    record = (
        db.query(EyeIdentification)
        .filter(EyeIdentification.id == identification_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="识别记录不存在",
        )

    # 检查权限：如果记录属于某个用户，只有该用户可以访问
    if record.user_id is not None and (
        current_user is None or record.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此记录",
        )

    try:
        # 获取图像路径
        image_path = record.image_path
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="图像文件不存在",
            )

        # 使用generate_gradcam函数生成热力图
        gradcam_img_bgr = generate_gradcam(
            image_path=image_path,
            model_path=None,  # 使用默认模型
            last_conv_layer_name=last_conv_layer_name,
            alpha=alpha,
        )

        # 将OpenCV格式的图像（BGR）编码为JPEG格式
        _, img_encoded = cv2.imencode(".jpg", gradcam_img_bgr)

        # 返回图像数据
        return Response(content=img_encoded.tobytes(), media_type="image/jpeg")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成Grad-CAM过程中发生错误: {str(e)}",
        )
