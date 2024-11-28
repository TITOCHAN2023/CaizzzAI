import hashlib

def hash_string(input_string: str) -> str:
    # 创建一个 SHA256 哈希对象
    hash_object = hashlib.sha256()
    
    # 更新哈希对象，使用字符串的字节表示
    hash_object.update(input_string.encode('utf-8'))
    
    # 返回十六进制格式的哈希值
    return hash_object.hexdigest()