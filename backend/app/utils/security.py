import secrets
import string


def generate_random_password(length=12):
    """生成随机密码"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length)) 