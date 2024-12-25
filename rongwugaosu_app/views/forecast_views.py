
from django.http import HttpRequest
from django.views import View
from rest_framework.decorators import api_view
from ..utils import uniform_response

# 该文件编写预测相关的接口
class ForecastView(View):

    @api_view(['POST'])
    def rate_flow(request: HttpRequest):
        # 业务代码  todo
        return uniform_response(True, "201",  "balabala", None)
