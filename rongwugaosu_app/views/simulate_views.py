import asyncio
import threading

from django.http import HttpRequest
from django.views import View

from ..sumo_simulate import simulate
from ..utils import is_simulating, uniform_response, set_simulating
from rest_framework.decorators import api_view


# 该文件编写仿真相关的接口
class SimulateView(View):

    # 保证在任意时刻，后台只运行一个仿真任务，不允许并发仿真
    @api_view(['POST'])
    def start_emulate(request: HttpRequest):
        if is_simulating():
            return uniform_response(False, 500, "正在仿真中，请稍后继续......", None)
        else:
            if set_simulating():
                # 异步业务处理 todo
                # args_dict 接收前端传来的参数，交给 simulate 方法进行处理
                args_dict =  {"args": {"step": 3600}}
                threading.Thread(target=simulate, kwargs=args_dict).start()
                return uniform_response(True, 200, "开始仿真", None)
            else:
                return uniform_response(False, 500, "正在仿真中，请稍后继续......", None)
