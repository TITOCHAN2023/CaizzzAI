from fastapi import APIRouter, HTTPException
from middleware.jwt import encode_token
from middleware.mysql import session
from middleware.mysql.models import UserSchema,ApiKeySchema
from ..model.response import StandardResponse
from ..model.request import LoginRequest, RegisterRequest
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from logger import logger
root_router = APIRouter(prefix="/root", tags=["root"])

    

@root_router.get("/", tags=["root"])
async def root() -> StandardResponse:
    return StandardResponse(
        code=0,
        status="success",
        message="Welcome to Caizzzai api!",
    )

@root_router.post("/login")
def login(request: LoginRequest):
    # 从数据库查询用户
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.username == request.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    # 验证密码
    if not check_password_hash(user.password_hash, request.password):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新最后登录时间
    with session() as conn:
        user.last_login = datetime.now()
        conn.commit()

    # 生成 JWT 令牌
    token = encode_token(uid=user.uid, level=int(user.is_admin))
    with session() as conn:
        api_key=conn.query(ApiKeySchema).filter(ApiKeySchema.uid==user.uid).first()
        api_key.api_key_secret=token 
        conn.commit()

    logger.info(token)
    return {"token": token}


@root_router.post("/register")
def register(request: RegisterRequest):
    with session() as conn:
        # 检查用户名是否已存在
        existing_user = conn.query(UserSchema).filter(UserSchema.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 哈希处理密码
        password_hash = generate_password_hash(request.password)

        # 创建新用户
        new_user = UserSchema(
            username=request.username,
            password_hash=password_hash,
            avatar=request.avatar,
            create_at=datetime.now(),
            is_admin=False  # 默认非管理员
        )
        conn.add(new_user)
        conn.commit()
        
        

    return {"message": "注册成功"}