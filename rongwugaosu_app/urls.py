from django.contrib.auth.views import LogoutView
from django.urls import path
from .views.login_views import LoginView
from .views.forecast_views import ForecastView
from .views.evaluate_views import EvaluateView
from .views.simulate_views import SimulateView

urlpatterns = [
    # 登陆相关
    path('user/login', LoginView.login, name='login'),  # 登陆功能接口
    path('user/get_portrayal', LoginView.get_portrayal, name='get_portrayal'),

    # 仿真相关
    path('simulate/start_emulate', SimulateView.start_emulate, name='start_emulate'),
    # path('simulation/select', SimulateView.select, name='select'),  # 交通仿真界面仿真接口
    path('simulation/central', SimulateView.central, name='central'),  # 路段中部流量折线图
    path('simulation/speed', SimulateView.speed, name='speed'),  # 路段平均速度折线图
    path('simulation/getRoadName', SimulateView.get_road_name, name='get_road_name'),  # 下拉获取路段名称
    path('simulation/getDirection', SimulateView.get_direction, name='get_direction'),  # 获取对应路段的运行方向

    # 预测相关
    path('prediction/rateFlow', ForecastView.rate_flow, name='rate_flow'),  # 流量预测折线图
    path('prediction/speed', ForecastView.speed, name='speed'),  # 速度预测折线图
    path('prediction/getData', ForecastView.get_date, name='get_date'),  # 获取场景对应可选日期

    # 评价相关
    path('evaluate/prediction', EvaluateView.prediction, name='prediction'),  # 路段X-流量变化折线图
    path('evaluate/trafficJam', EvaluateView.traffic_jam, name='traffic_jam'),  # 路段X-拥堵持续时间柱状图（+曲线图）
    path('evaluate/reliableIndex', EvaluateView.reliable_index, name='reliable_index'),  # 路段X-行驶可靠指数折线图
    path('evaluate/avgSpeed', EvaluateView.avg_speed, name='avg_speed'),  # 路段X-平均车速折线图
    path('evaluate/serviceLevel', EvaluateView.service_level, name='service_level'),  # 路段X-路段服务水平折线图
    path('evaluate/serviceLevelAll', EvaluateView.service_level_all, name='service_level_all'),  # 全路段服务水平折线图
    path('evaluate/trafficJamAll', EvaluateView.traffic_jam_all, name='traffic_jam_all'),  # 全路段交通拥堵率折线图
    path('evaluate/jamMileage', EvaluateView.jam_mileage, name='jam_mileage'),  # 全路段拥堵里程比例柱状图（+曲线图）
    path('evaluate/getDate', EvaluateView.get_date, name='get_date'),  # 获取评价界面可选择的日期列表
]
