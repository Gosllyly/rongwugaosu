import threading

from django.http import JsonResponse
from django.core.cache import caches

# 初始化仿真标记
flag = "is_emulating"
cache = caches['default']
cache.set(flag, False)

# 设置锁
lock = threading.Lock()


# 统一处理 API 请求
def uniform_response(success, code, message, data):
    if data is None:
        data = {}
    response = {
        "success": success,
        "code": code,
        "message": message,
        "data": data,
    }
    return JsonResponse(response)


# 判断是否正在仿真
def is_emulating():
    return cache.get(flag)


# 设置正在仿真标记位
def set_emulating():
    with lock:
        if cache.get(flag):
            return False
        else:
            cache.set(flag, True)
            return True


# 恢复标记位
def reset_emulating():
    cache.set(flag, False)
