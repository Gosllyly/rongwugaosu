from django.views import View
from django.http import HttpRequest
from ..utils import uniform_response
from rest_framework.decorators import api_view


# 该文件编写 登录退出相关的接口
class LoginView(View):

    @api_view(['POST'])
    def login(request: HttpRequest):
        # 从请求体里面获取参数
        username = request.data.get('username')
        password = request.data.get('password')
        if (username == "admin") & (password == "admin"):
            return uniform_response(True, "200", "login successfully", None)
        elif username != "admin":
            return uniform_response(True, "201", "用户名不存在", None)
        else:
            return uniform_response(True, "201", "密码错误", None)

    @api_view(['GET'])
    def get_portrayal(request: HttpRequest):
        # 从 URL 中获取参数
        username = request.GET.get('username')
        if username == "admin":
            data = {
                "name": username,
                "height": 180,
                "face score": "A",
                "wealth": "10 billion"
            }
            return uniform_response(True, "200", "", data)
        else:
            return uniform_response(True, "401", username + "'s portrayal is not exist.", None)
