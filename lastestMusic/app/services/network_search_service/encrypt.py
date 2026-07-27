import subprocess
import json
import random
import string
import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def generate_random_key(length=16):
    """生成16位随机密钥（和浏览器一致）"""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(length))


def aes_encrypt(text, key):
    """AES-CBC 加密，返回 Base64 字符串"""
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, "0102030405060708".encode('utf-8'))
    return base64.b64encode(cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))).decode('utf-8')


def get_enc_sec_key(random_key):
    """调用 Node.js RSA.js 获取 encSecKey"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rsa_js_path = os.path.join(script_dir, 'RSA.js')

    result = subprocess.run(
        ['node', rsa_js_path, random_key],
        capture_output=True,
        text=True,
        cwd=script_dir
    )

    if result.returncode != 0:
        raise RuntimeError(f"RSA.js 执行失败: {result.stderr}")

    lines = result.stdout.strip().split('\n')
    # 取最后一行（去掉调试信息）
    return lines[-1] if lines else None


def get_encrypted_params(song_id):
    """
    输入 song_id，输出 params 和 encSecKey

    Args:
        song_id: 歌曲ID (int)

    Returns:
        dict: {'params': 'xxx', 'encSecKey': 'xxx', 'randomKey': 'xxx'}
    """
    # 1. 构造请求 JSON
    json_str = json.dumps({
        "ids": f"[{song_id}]",
        "level": "exhigh",
        "encodeType": "aac"
    }, separators=(',', ':'))

    # 2. 生成随机密钥
    random_key = generate_random_key(16)

    # 3. 第一层 AES（固定密钥）
    enc_text = aes_encrypt(json_str, "0CoJUm6Qyw8W8jud")

    # 4. 第二层 AES（随机密钥）
    enc_text = aes_encrypt(enc_text, random_key)

    # 5. RSA 加密（调用 Node.js）
    enc_sec_key = get_enc_sec_key(random_key)

    return {
        'params': enc_text,
        'encSecKey': enc_sec_key,
        'randomKey': random_key
    }


if __name__ == "__main__":
    # 测试
    song_id = 3383959812
    result = get_encrypted_params(song_id)

    print("=" * 60)
    print("🎵 歌曲ID:", song_id)
    print("=" * 60)
    print("params:")
    print(result['params'])
    print()
    print("encSecKey:")
    print(result['encSecKey'])
    print()
    print("randomKey:")
    print(result['randomKey'])
    print("=" * 60)
