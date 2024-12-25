from django.http import HttpRequest
from django.views import View
from ..utils import is_emulating, uniform_response, set_emulating, reset_emulating
from rest_framework.decorators import api_view


# 该文件编写仿真相关的接口
class EmulateView(View):
    @api_view(['POST'])
    def start_emulate(request: HttpRequest):
        if is_emulating():
            return uniform_response(False, 500, "正在仿真中，请稍后继续......", None)
        else:
            if set_emulating():
                # 异步业务处理 todo
                return uniform_response(True, 200, "开始仿真", None)
            else:
                return uniform_response(False, 500, "正在仿真中，请稍后继续......", None)
