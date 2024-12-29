from django.http import HttpRequest
from django.views import View
from rest_framework.decorators import api_view
from ..utils import uniform_response
from ..MainCode.staeformer_prediction.model.predict import *


# 该文件编写预测相关的接口
class ForecastView(View):

    @api_view(['POST'])
    def rate_flow(request: HttpRequest):
        date = request.data.get('date')
        roadName = request.data.get('roadName')
        direction = request.data.get('direction')
        type = request.data.get('type')
        startTime = request.data.get('startTime')
        time_list, prediction_list = predict_flow(date, roadName, direction, type, int(startTime))
        data = {
            "time": time_list,
            "prediction": prediction_list,
        }
        return uniform_response(True, "200", "成功", data)

    @api_view(['POST'])
    def speed(request: HttpRequest):
        date = request.data.get('date')
        roadName = request.data.get('roadName')
        direction = request.data.get('direction')
        type = request.data.get('type')
        startTime = request.data.get('startTime')
        time_list, speed_list = predict_speed(date, roadName, direction, type, startTime)
        data = {
            "time": time_list,
            "prediction": speed_list,
        }
        return uniform_response(True, "200", "成功", data)

    @api_view(['GET'])
    def get_date(request: HttpRequest):
        type = request.GET.get('type')
        data_0 = ["2023-09-14", "2024-01-05", "2024-02-05", "2024-03-05"]
        data_1 = ["2023-09-17", "2024-01-14", "2024-02-03", "2024-03-03", "2023-09-29"]
        data_2 = ["2023-09-29"]
        if type == 0:  # 工作日
            return uniform_response(True, "200", "成功", data_0)
        elif type == 1:  # 周末
            return uniform_response(True, "200", "成功", data_1)
        else:  # 节假日
            return uniform_response(True, "200", "成功", data_2)
