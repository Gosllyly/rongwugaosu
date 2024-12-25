from django.http import JsonResponse

## 统一处理 API 请求
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
