from django.http import HttpRequest
from django.views import View
from ..utils import uniform_response
from rest_framework.decorators import api_view
from ..MainCode.staeformer_evaluation.metrics import *


# 该文件编写评价相关的接口
class EvaluateView(View):
    @api_view(['GET'])
    def prediction(request: HttpRequest):
        date = request.GET.get('date')
        day_flow_data = select_day_data(full_year_flow_data, date)
        direction = request.GET.get('direction')
        roadName = request.GET.get('roadName')
        time_list, percentage_list = calculate_flow_difference(day_flow_data, direction, roadName)
        return uniform_response(True, 200, "成功", {"time": time_list, "percentage": percentage_list})

    @api_view(['GET'])
    def traffic_jam(request: HttpRequest):
        date = request.GET.get('date')
        day_speed_data = select_day_data(full_year_speed_data, date)
        spi = calculate_spi(day_speed_data)
        direction = request.GET.get('direction')
        roadName = request.GET.get('roadName')
        time_list, duration_list = calculate_congestion_duration(spi, direction, roadName)
        return uniform_response(True, 200, "成功", {"time": time_list, "duration": duration_list})

    @api_view(['GET'])
    def reliable_index(request: HttpRequest):
        date = request.GET.get('date')
        day_speed_data = select_day_data(full_year_speed_data, date)
        direction = request.GET.get('direction')
        roadName = request.GET.get('roadName')
        time_list, index_num_list = calculate_spi_select(day_speed_data, direction, roadName)
        return uniform_response(True, 200, "成功", {"time": time_list, "indexNum": index_num_list})

    @api_view(['GET'])
    def avg_speed(request: HttpRequest):
        date = request.GET.get('date')
        day_speed_data = select_day_data(full_year_speed_data, date)
        direction = request.GET.get('direction')
        roadName = request.GET.get('roadName')
        time_list, speed_list = calculate_average_speed(day_speed_data, direction, roadName)
        return uniform_response(True, 200, "成功", {"time": time_list, "speed": speed_list})

    @api_view(['GET'])
    def service_level(request: HttpRequest):
        date = request.GET.get('date')
        day_flow_data = select_day_data(full_year_flow_data, date)
        direction = request.GET.get('direction')
        roadName = request.GET.get('roadName')
        time_list, level_list = calculate_service_level_select(day_flow_data, direction, roadName)
        return uniform_response(True, 200, "成功", {"time": time_list, "level": level_list})

    @api_view(['GET'])
    def service_level_all(request: HttpRequest):
        date = request.GET.get('date')
        day_flow_data = select_day_data(full_year_flow_data, date)
        direction = request.GET.get('direction')
        service_level = calculate_service_level(day_flow_data)
        road_lengths, t95_times, free_flow_times = get_road_metrics(direction)
        time_list, los_all_list = calculate_los_all(service_level, road_lengths)
        return uniform_response(True, 200, "成功", {"time": time_list, "level": los_all_list})

    @api_view(['GET'])
    def traffic_jam_all(request: HttpRequest):
        date = request.GET.get('date')
        day_speed_data = select_day_data(full_year_speed_data, date)
        spi = calculate_spi(day_speed_data)
        direction = request.GET.get('direction')
        road_lengths, t95_times, free_flow_times = get_road_metrics(direction)
        time_list, percentage_list = calculate_tcr(spi, road_lengths)
        return uniform_response(True, 200, "成功", {"time": time_list, "percentage": percentage_list})

    @api_view(['GET'])
    def jam_mileage(request: HttpRequest):
        date = request.GET.get('date')
        day_speed_data = select_day_data(full_year_speed_data, date)
        spi = calculate_spi(day_speed_data)
        direction = request.GET.get('direction')
        road_lengths, t95_times, free_flow_times = get_road_metrics(direction)
        time_list, percentage_list = calculate_congestion_distance_ratio(spi, road_lengths)
        return uniform_response(True, 200, "成功", {"time": time_list, "percentage": percentage_list})

    @api_view(['GET'])
    def get_date(request: HttpRequest):
        date_list = select_not_null(full_year_flow_data, full_year_speed_data)
        return uniform_response(True, 200, "成功", date_list)
