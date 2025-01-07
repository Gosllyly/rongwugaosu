import asyncio
import threading

from django.http import HttpRequest
from django.views import View

from ..sumo_simulate import simulate
from ..utils import is_simulating, uniform_response, set_simulating
from rest_framework.decorators import api_view
from django.core.cache import cache
import os
import xml.etree.ElementTree as ET
from ..MainCode.staeformer_prediction.model.predict import time_list_process
from ..MainCode.staeformer_evaluation.metrics import traffic_demand_data


# 该文件编写仿真相关的接口
class SimulateView(View):

    # 保证在任意时刻，后台只运行一个仿真任务，不允许并发仿真
    @api_view(['POST'])
    def start_emulate(request: HttpRequest):
        simulate_type = request.data.get('type')  # 类型，代表是自定义参数设置的仿真，1代表是典型场景的仿真
        if simulate_type == 0:
            step = request.data.get('duration')  # 仿真时长
            selection = request.data.get('selection')  # 时段选择，传0代表从0点到1点，传1代表从1点到2点，以此类推
        else:
            step = 3600
            selection = None  # 时段选择，传0代表从0点到1点，传1代表从1点到2点，以此类推
        roadName = request.data.get('roadName')  # 路段名称
        speedLimit = request.data.get('speedLimit')  # 路段限速
        direction = request.data.get('direction')  # 运行方向,0代表上行，1代表下行
        amplitude = request.data.get('amplitude')  # 超速幅度
        trafficDem = request.data.get('trafficDem')  # 交通需求
        # 将上下行方向和路段名称存入缓存
        print(type(direction))
        cache.set('direction', int(direction))
        cache.set('roadName', roadName)
        if is_simulating():
            return uniform_response(False, 201, "正在仿真中，请稍后继续......", None)
        else:
            if set_simulating():
                # 异步业务处理 todo
                # args_dict 接收前端传来的参数，交给 simulate 方法进行处理
                args_dict = {
                    "args": {"step": step, "roadName": roadName, "speedLimit": speedLimit, "direction": direction,
                             "amplitude": amplitude, "trafficDem": trafficDem, "type": simulate_type,
                             "selection": selection}}
                threading.Thread(target=simulate, kwargs=args_dict).start()
                return uniform_response(True, 200, "开始仿真", None)
            else:
                return uniform_response(False, 201, "正在仿真中，请稍后继续......", None)

    # @api_view(['POST'])
    # def select(request: HttpRequest):
    #     return uniform_response(True, 200, "成功", None)

    @api_view(['GET'])
    def central(request: HttpRequest):
        direction_dict = {0: "S", 1: "X"}
        direction = cache.get('direction')
        roadName = cache.get('roadName')
        print(direction, roadName)
        # 需要改成绝对路径
        current_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = current_dir_path + f"/sumo/output/{direction_dict[direction]}/{direction_dict[direction]}{roadName}"
        # file_path = f"../sumo/output/{direction_dict[direction]}/{direction_dict[direction]}{roadName}"
        # file_path = "C:/Users/m1317/Desktop/所有项目/沧州高速公路/rongwugaosu-master-v1/rongwugaosu_app/sumo/output/S/SK628"
        # print("file_path", file_path)
        # print(os.path.exists(file_path))
        # print(os.path.isdir(file_path))
        if os.path.isdir(file_path):
            # 列出文件夹中的所有文件和子目录
            files_and_dirs = os.listdir(file_path)
            # 仅获取文件的列表
            files = [f for f in files_and_dirs if os.path.isfile(os.path.join(file_path, f))]
            file_count = len(files)
            print(f"目录 '{file_path}' 存在，包含 {file_count} 个文件。")
            # 逐一操作每个文件
            files_list = []
            for file_name in files:
                files_list.append(os.path.join(file_path, file_name))
            traffic_volume_list, time_list = SimulateView.add_flow_from_multiple_xml(files_list)
            return uniform_response(True, 200, "成功", {"time": time_list, "trafficVolume": traffic_volume_list})
        else:
            return uniform_response(False, 201, "正在仿真中，请稍后继续......", None)
        # time_list = ["00:00", "00:05", "00:10"],
        # traffic_volume_list = [800, 600, 1000]

    @api_view(['GET'])
    def speed(request: HttpRequest):
        direction_dict = {0: "S", 1: "X"}
        direction = cache.get('direction')
        roadName = cache.get('roadName')
        # 需要改成绝对路径 todo
        # file_path = f"../sumo/output/{direction_dict[direction]}/{direction_dict[direction]}{roadName}"
        current_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = current_dir_path + f"/sumo/output/{direction_dict[direction]}/{direction_dict[direction]}{roadName}"
        # file_path = "C:/Users/m1317/Desktop/所有项目/沧州高速公路/rongwugaosu-master-v1/rongwugaosu_app/sumo/output/S/SK628"
        if os.path.exists(file_path) and os.path.isdir(file_path):
            # 列出文件夹中的所有文件和子目录
            files_and_dirs = os.listdir(file_path)
            # 仅获取文件的列表
            files = [f for f in files_and_dirs if os.path.isfile(os.path.join(file_path, f))]
            file_count = len(files)
            print(f"目录 '{file_path}' 存在，包含 {file_count} 个文件。")
            # 逐一操作每个文件
            files_list = []
            for file_name in files:
                files_list.append(os.path.join(file_path, file_name))
            speed_list, time_list = SimulateView.find_max_values(files_list)
            return uniform_response(True, 200, "成功", {"time": time_list, "speed": speed_list})
        else:
            return uniform_response(False, 201, "正在仿真中，请稍后继续......", None)

    @api_view(['GET'])
    def get_road_name(request: HttpRequest):
        road_list = ["K628", "K633", "K654", "K660", "K664", "K677", "K678", "K679", "K680", "K681", "K682", "K688",
                     "K629"],
        return uniform_response(True, 200, "成功", road_list)

    @api_view(['GET'])
    def get_direction(request: HttpRequest):
        roadName = request.GET.get('roadName')  # 路段名称
        road_dirction_dict = {"K628": ["0", "1"], "K633": ["0", "1"], "K654": ["0"], "K660": ["0", "1"],
                              "K664": ["0", "1"], "K677": ["0", "1"], "K678": ["0", "1"], "K679": ["0", "1"],
                              "K680": ["0", "1"], "K681": ["0"], "K682": ["0", "1"], "K688": ["0"], "K629": ["1"]}
        return uniform_response(True, 200, "成功", road_dirction_dict[roadName])

    @staticmethod
    def parse_xml(file_path, value_name):
        """读取 XML 文件并提取所有 <value> 元素的整数值"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        intervals = root.findall('interval')
        # for item in intervals:
        #     print(value_name,item.find(value_name))
        return [int(float(item.get(value_name))) for item in intervals], len(intervals)

    @staticmethod
    def add_flow_from_multiple_xml(files_list, value_name="flow"):
        """从多个 XML 文件中相加对应 <value> 元素的值"""
        # 初始化一个空列表，用于存储累加结果
        total_values = None
        time_list = []
        for file_path in files_list:
            current_values, time_num = SimulateView.parse_xml(file_path, value_name)
            time_list = time_list_process("00:05", time_num - 1, 5)
            if total_values is None:
                # 如果是第一个文件，初始化 total_values
                total_values = current_values
            else:
                # 检查所有文件的结构是否一致
                if len(total_values) != len(current_values):
                    raise ValueError("XML 文件的结构不匹配")
                # 对应项相加
                total_values = [sum(x) for x in zip(total_values, current_values)]
        return [x / 12 for x in total_values], time_list

    @staticmethod
    def find_max_values(files_list, value_name="speed"):
        """从多个 XML 文件中找到对应 <value> 的最大值"""
        max_values = None
        time_list = []
        for file_path in files_list:
            current_values, time_num = SimulateView.parse_xml(file_path, value_name)
            time_list = time_list_process("00:05", time_num - 1, 5)
            if max_values is None:
                # 初始化 max_values
                max_values = current_values
            else:
                # 检查所有文件的结构是否一致
                if len(max_values) != len(current_values):
                    raise ValueError("XML 文件的结构不匹配")
                # 取最大值
                max_values = [int(max(x) * 3.6) for x in zip(max_values, current_values)]
        return max_values, time_list

    @api_view(['GET'])
    def get_traffic_flow(request: HttpRequest):
        # time_dict = {0: "工作日", 1: "周末", 2: "节假日"}
        time_type = int(request.GET.get('type'))
        selection = int(request.GET.get('selection'))
        # traffic_flow = traffic_demand_data.loc[f"{time_type}-{time_type + 1}", time_dict[selection]]
        # print(type(traffic_demand_data))
        traffic_flow = traffic_demand_data.iloc[time_type, selection + 1]
        return uniform_response(True, 200, "成功", [traffic_flow])
