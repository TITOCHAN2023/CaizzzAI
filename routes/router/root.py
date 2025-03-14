import base64
from fastapi import APIRouter, HTTPException
from middleware.jwt import encode_token
from middleware.otp import generate_otp, verify_otp
from middleware.mysql import session
from middleware.mysql.models import UserSchema,ApiKeySchema
from middleware.hash.hash import hash_string
from ..model.response import StandardResponse
from ..model.request import LoginRequest, RegisterRequest,ResetUserRequest, WXRegisterRequest
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from logger import logger
from env import OTP_SECRET,OTP_SECRET_2,API_KEY_HOST,API_KEY_ROOT_AUTH,FREE_USAGE,WX_APPID,WX_APPSECRET
import requests


root_router = APIRouter(prefix="/root", tags=["root"])

    

@root_router.get("/", tags=["root"])
async def root() -> StandardResponse:
    otp=generate_otp(OTP_SECRET)
    logger.info("OTP code: "+otp)
    return StandardResponse(
        code=0,
        status="success",
        message="Welcome to Caizzzai api!",
    )

@root_router.post("/login")
def login(request: LoginRequest):
    is_admin=False
    # 从数据库查询用户
    with session() as conn:
        user = conn.query(UserSchema).filter(UserSchema.username == request.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    # 验证密码
    if not check_password_hash(user.password_hash, request.password):
        raise HTTPException(status_code=401, detail="密码错误")
    is_admin=user.is_admin
    # 更新最后登录时间
    with session() as conn:
        user.last_login = datetime.now()
        conn.commit()

    # 生成 JWT 令牌
    token = encode_token(uid=user.uid, level=int(user.is_admin))
    with session() as conn:
        api_key=conn.query(ApiKeySchema).filter(ApiKeySchema.uid==user.uid).first()
        if not api_key:
            api_key = ApiKeySchema(uid=user.uid, api_key_secret=token)
            conn.add(api_key)
        else:
            api_key.api_key_secret = token
        conn.commit()
    
    logger.info(token)

    auth=""
 
    responseLogin=requests.post(API_KEY_HOST+"/api/login",json={"username":request.username,"password":"chatnio123456!@#"})
    response1json=responseLogin.json()

    if response1json["status"]==False:

        responseRisgister=requests.post(API_KEY_HOST+"/api/register",json={"username":request.username,"password":"chatnio123456!@#","repassword":"chatnio123456!@#","email":hash_string(request.username+request.password)+"@titochan.top","code":""})
        response2json=responseRisgister.json()

        if response2json["status"]==True:
            auth=response2json["token"]

            responseUserList = requests.get(
                f"{API_KEY_HOST}/api/admin/user/list?page=0&search={request.username}",
                headers={
                "sec-ch-ua-platform": "macOS",
                "Authorization": f"{API_KEY_ROOT_AUTH}",
                "Referer": f"{API_KEY_HOST}/admin/users",
                }
            )
            responseUserListJson = responseUserList.json()
            Id = responseUserListJson["data"][0]["id"]
            responseQuota = requests.post(
                f"{API_KEY_HOST}/api/admin/user/quota",
                headers={
                "Authorization": f"{API_KEY_ROOT_AUTH}",
                "Referer": f"{API_KEY_HOST}/admin/users",
                "Content-Type": "application/json"
                },
                json={"id":Id,"quota":int(FREE_USAGE),"override":False}
            )
            responseQuotaJson = responseQuota.json()
            logger.info(responseQuotaJson)
    else:
        auth=response1json["token"]
    
    if auth=="":
        auth="账号出现问题 请联系管理员"
    else:
        responseApikey=requests.get(API_KEY_HOST+"/api/apikey",headers={"Authorization":auth})
        response1json=responseApikey.json()
        if response1json["status"]==False:
            auth="账号出现问题 请联系管理员"
        else:
            auth=response1json["key"]

    return {"token": token,"avatar":user.avatar,"key":auth,"isadmin":is_admin}


@root_router.post("/register")
def register(request: RegisterRequest):

    # 验证OTP
    if not  request.otp==OTP_SECRET_2: #verify_otp(OTP_SECRET, request.otp):
        raise HTTPException(status_code=401, detail="验证码错误")

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
            avatar=request.avatar if request.avatar else "https://titochan.top/gpt/media/2fbc381a43bd4195db06ff448f8cf9679fec08fcdc9c4358d51e6061.png",
            create_at=datetime.now(),
            is_admin=False  # 默认非管理员
        )
        conn.add(new_user)
        conn.commit()
        
        

    return {"status": "ok"}


@root_router.post("/wxlogin")
def wxlogin(request: WXRegisterRequest):
    # 验证微信登录
    response=requests.get(f"https://api.weixin.qq.com/sns/jscode2session?appid={WX_APPID}&secret={WX_APPSECRET}&js_code={request.js_code}&grant_type=authorization_code")
    responseJson=response.json()
    if "errcode" in responseJson:
        if responseJson["errcode"]!=0:
            logger.error(responseJson)
            raise HTTPException(status_code=401, detail="微信登录失败")
    encoded = base64.b64encode(responseJson['openid'].encode()).decode()
    responseJson['openid']=encoded[:24]
    with session() as conn:
        # 检查用户是否存在 存在则登录 不存在则注册
        user = conn.query(UserSchema).filter(UserSchema.username == responseJson['openid']).first()
        if not user:
            response=register(request=RegisterRequest(otp=OTP_SECRET_2,username=responseJson['openid'],password=responseJson['openid']))
            if response["status"]!="ok":
                raise HTTPException(status_code=401, detail="注册失败")
        
    response=login(request=LoginRequest(username=responseJson['openid'],password=responseJson['openid']))


    return response


@root_router.post("/reset_user")
def reset_user(request:ResetUserRequest):
    with session() as conn:
        user =conn.query(UserSchema).filter(UserSchema.username==request.originUsername).first()

        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
    
        if not check_password_hash(user.password_hash, request.originPassword) or not verify_otp(OTP_SECRET, request.otp):
            raise HTTPException(status_code=401, detail="密码或验证码错误")
            
        user.username=request.username
        user.password_hash=generate_password_hash(request.password)
        logger.info(user.password_hash)
        if request.avatar:
            user.avatar=request.avatar
        user.last_login = datetime.now()
        conn.commit()

    return {"message": "更改成功"}