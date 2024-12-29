# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 13:27:44 2024

@author: MH
"""
import pandas as pd
from datetime import datetime
import sqlite3


def select_day_data(data, target_date):
    data['时间'] = pd.to_datetime(data['时间'])
    day_data = data[data['时间'].datetime.strftime('%Y-%m-%d') == target_date]
    return day_data


def select_not_null(flow_data, speed_data):
    flow_filtered_times = set(flow_data[
        flow_data['断面2流量'].notna() & flow_data['断面3流量'].notna() & flow_data[
            '断面4流量'].notna() & flow_data['断面5流量'].notna() & flow_data[
            '断面6流量'].notna() & flow_data['断面7流量'].notna() & flow_data[
            '断面8流量'].notna()]['时间'].datetime.strftime(
        '%Y-%m-%d'))
    speed_filtered_times = set(
        speed_data[speed_data['Column_1'].notna() & speed_data['Column_2'].notna() & speed_data['Column_3'].notna() &
                   speed_data['Column_4'].notna() & speed_data['Column_5'].notna() & speed_data['Column_6'].notna() &
                   speed_data['Column_7'].notna()]['时间'].datetime.strftime('%Y-%m-%d'))

    common_times = flow_filtered_times.intersection(speed_filtered_times)

    # 将结果转换为列表并输出
    result_times = list(common_times)
    return result_times


# 读取sqlite数据库
def read_sqlite():
    # 连接到 SQLite 数据库
    conn = sqlite3.connect('up_flow_and_speed.sqlite3')
    # 使用 Pandas 读取数据并存储到 DataFrame
    full_year_flow_data = pd.read_sql_query('SELECT * FROM "上行流量"', conn)
    full_year_speed_data = pd.read_sql_query('SELECT * FROM "上行速度"', conn)
    # 关闭数据库连接
    conn.close()
    return full_year_flow_data, full_year_speed_data


# 全局变量
# 0表示上行，1代表下行
section_dict = {0: {'K628': 0, 'K633': 1, 'K660': 2, 'K664': 3, 'K679': 4, 'K681': 5, 'K682': 6},
                1: {'K682': 0, 'K679': 1, 'K664': 2, 'K660': 3, 'K633': 4, 'K629': 5, 'K628': 6}}
full_year_flow_data, full_year_speed_data = read_sqlite()


def get_road_metrics(direction):
    """
    获取道路相关参数，根据方向选择上行或下行。
    Args:
        direction (str): 方向，可选值为 "upstream" 或 "downstream"，默认为 "upstream"。
    Returns:
        tuple: 包括道路长度列表、t95 时间列表、自由流时间列表。
    """
    if direction == 1:
        road_lengths = [0.68, 4.755, 26.865, 4.066, 15.134, 2.45, 0.5]
        t95_times = [0.6474, 7.2666, 35.5044, 3.1662, 12.3024, 1.7388, 0.4614]
        free_flow_times = [0.34, 2.3775, 13.4325, 2.033, 7.567, 1.225, 0.25]
    elif direction == 0:
        road_lengths = [0.55, 2.95, 15.116, 4.064, 26.85, 4.27, 0.5]
        t95_times = [0.3833, 2.7333, 12.3333, 3.1333, 20.4, 3.35, 0.4833]
        free_flow_times = [0.2833, 1.4833, 7.55, 2.0333, 13.4333, 2.1333, 0.25]
    else:
        raise ValueError("Invalid direction. Please choose 'upstream' or 'downstream'.")
    return road_lengths, t95_times, free_flow_times


def time_trans(datetime_str):
    # 定义日期时间格式并解析字符串
    datetime_obj = datetime.strptime(datetime_str, "%Y/%m/%d %H:%M:%S")
    # 提取小时和分钟，并格式化为"HH:MM"格式
    return datetime_obj.strftime("%H:%M")


def calculate_flow_difference(data, direction, roadName):
    """
    计算各路段流量差。
    输入：
        data: 包含流量信息的 DataFrame，列名包括 '时间' 和 '断面1流量' 至 '断面8流量'。
    输出：
        result: 包含每个路段流量差的 DataFrame，列名包括 '时间' 和 '路段1流量差' 至 '路段7流量差'。
    """
    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    section_index = section_dict[direction][roadName] + 2
    return time_list, (data[f'断面{section_index + 1}流量'] - data[f'断面{section_index}流量']).tolist()


def calculate_service_level(data):
    """
    计算各路段服务水平。

    输入：
        data: 包含流量信息的 DataFrame，列名包括 '时间' 和 '断面1流量' 至 '断面7流量'。
    输出：
        result: 包含每个路段服务水平的 DataFrame，列名包括 '时间' 和 '路段1服务水平' 至 '路段7服务水平'。
    """
    result = pd.DataFrame()
    result['时间'] = data['时间']
    for i in range(1, 8):
        hourly_flow = data[f'断面{i}流量'] * 12
        result[f'路段{i}服务水平'] = hourly_flow / 2200
    return result


def calculate_service_level_select(data, direction, roadName):
    """
    计算各路段服务水平。
    输入：
        data: 包含流量信息的 DataFrame，列名包括 '时间' 和 '断面1流量' 至 '断面7流量'。
    输出：
        result: 包含每个路段服务水平的 DataFrame，列名包括 '时间' 和 '路段1服务水平' 至 '路段7服务水平'。
    """
    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    section_index = section_dict[direction][roadName] + 2
    level_list = (data[f'断面{section_index}流量'] * 12 / 2200).tolist()
    return time_list, level_list


def calculate_average_speed(speed_data, direction, roadName):
    """
    计算各路段平均速度。

    输入：
        speed_data: 包含速度信息的 DataFrame，列名包括 '时间' 和 'Column_1' 至 'Column_7'。
    输出：
        result: 包含每个路段平均速度的 DataFrame，列名包括 '时间' 和 '路段1平均速度' 至 '路段7平均速度'。
    """
    time_list = []
    for datetime_str in speed_data['时间']:
        time_list.append(time_trans(datetime_str))
    section_index = section_dict[direction][roadName] + 1
    return time_list, speed_data[f'Column_{section_index}'].tolist()


def calculate_spi(data):
    """
    计算各路段 SPI 指数。

    输入：
        data: 包含速度信息的 DataFrame，列名包括 '时间' 和其他速度列。
    输出：
        result: 包含每个路段 SPI 指数的 DataFrame，列名包括 '时间' 和 '路段1SPI' 至 '路段7SPI'。
    """
    speed_to_spi = [(150, 80, 0, 1), (80, 60, 1, 2), (60, 50, 2, 3), (50, 35, 3, 4), (35, 10, 4, 5), (10, 0, 0, 0)]

    def spi_value(v):
        for upper, lower, upper_spi, lower_spi in speed_to_spi:
            if lower < v <= upper:
                return (v - lower) / (upper - lower) * (upper_spi - lower_spi) + lower_spi
        return 0

    result = pd.DataFrame()
    result['时间'] = data['时间']
    for i, col in enumerate(data.columns):
        if col != '时间':
            result[f'路段{i}SPI'] = data[col].apply(spi_value)
    return result


def calculate_spi_select(data, direction, roadName):
    """
    计算各路段 SPI 指数。

    输入：
        data: 包含速度信息的 DataFrame，列名包括 '时间' 和其他速度列。
    输出：
        result: 包含每个路段 SPI 指数的 DataFrame，列名包括 '时间' 和 '路段1SPI' 至 '路段7SPI'。
    """
    speed_to_spi = [(150, 80, 0, 1), (80, 60, 1, 2), (60, 50, 2, 3), (50, 35, 3, 4), (35, 10, 4, 5), (10, 0, 0, 0)]

    def spi_value(v):
        for upper, lower, upper_spi, lower_spi in speed_to_spi:
            if lower < v <= upper:
                return (v - lower) / (upper - lower) * (upper_spi - lower_spi) + lower_spi
        return 0

    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    section_index = section_dict[direction][roadName] + 1
    return time_list, (data[section_index].apply(spi_value)).tolist()


def calculate_congestion_duration(spi_data, direction, roadName, time_interval=5):
    """
    计算各路段拥堵持续时间。

    输入：
        spi_data: 包含 SPI 数据的 DataFrame，列名包括 '时间' 和 '路段1SPI' 至 '路段7SPI'。
        time_interval: 时间间隔，单位为分钟。
    输出：
        result: 包含各路段拥堵持续时间的 DataFrame，列名包括 '时间' 和 '路段1拥堵持续时间' 至 '路段7拥堵持续时间'。
    """

    def daily_congestion(spi_series, time_series):
        congestion_duration = 0
        durations = []
        current_date = time_series.iloc[0].date()
        for time, spi in zip(time_series, spi_series):
            if time.date() != current_date:
                congestion_duration = 0
                current_date = time.date()
            if spi >= 3:
                congestion_duration += time_interval
            else:
                congestion_duration = 0
            durations.append(congestion_duration)
        return durations

    time_list = []
    section_index = section_dict[direction][roadName] + 1
    for datetime_str in spi_data['时间']:
        time_list.append(time_trans(datetime_str))
    duration_list = daily_congestion(spi_data[f'路段{section_index}SPI'], spi_data['时间'])
    return time_list, duration_list


def calculate_tbi(speed_data, road_lengths, t95_times, free_flow_times):
    """
    计算各路段 TBI 指标。

    输入：
        speed_data: 包含速度信息的 DataFrame，列名包括 '时间' 和 'Column_1' 至 'Column_7'。
        road_lengths: 路段长度列表。
        t95_times: 各路段的 95% 行程时间列表。
        free_flow_times: 各路段的自由流时间列表。
    输出：
        result: 包含每个路段 TBI 的 DataFrame，列名包括 '时间' 和 '路段1TBI' 至 '路段7TBI'。
    """

    def average_travel_time(length, speed):
        return (length / speed) * 60 if speed > 0 else None

    def tbi_value(t95, avg_time, free_flow):
        return (t95 - avg_time) / free_flow if avg_time and free_flow > 0 else None

    result = pd.DataFrame()
    result['时间'] = speed_data['时间']
    for i, (length, t95, free_flow) in enumerate(zip(road_lengths, t95_times, free_flow_times), start=1):
        result[f'路段{i}TBI'] = speed_data[f'Column_{i}'].apply(
            lambda speed: tbi_value(t95, average_travel_time(length, speed), free_flow)
        )
    return result


def calculate_los_all(data, road_lengths):
    """
    计算全路段服务水平 (LoS_all)。

    输入：
        data: 包含各路段服务水平的 DataFrame。
        road_lengths: 路段长度列表。
    输出：
        los_all: 包含全路段服务水平的 DataFrame，列名包括 '时间' 和 'LoS_all'。
    """
    metrics = ['路段1服务水平', '路段2服务水平', '路段3服务水平', '路段4服务水平', '路段5服务水平', '路段6服务水平',
               '路段7服务水平']
    L_sum = sum(road_lengths)
    los_all = pd.DataFrame()
    los_all['LoS_all'] = sum(data[metric] * road_lengths[i] for i, metric in enumerate(metrics)) / L_sum
    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    return time_list, los_all['LoS_all'].tolist()


def calculate_congestion_distance_ratio(data, road_lengths):
    """
    计算拥堵距离比率 (R)。

    输入：
        data: 包含各路段 SPI 数据的 DataFrame。
        road_lengths: 路段长度列表。
    输出：
        congestion_distance_ratio: 包含拥堵距离比率的 DataFrame，列名包括 '时间' 和 'R'。
    """
    metrics = ['路段1SPI', '路段2SPI', '路段3SPI', '路段4SPI', '路段5SPI', '路段6SPI', '路段7SPI']
    L_sum = sum(road_lengths)
    congestion_distance_ratio = pd.DataFrame()
    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    congestion_distance_ratio['R'] = [
        sum(road_lengths[i] if data[metric].iloc[j] >= 3 else 0 for i, metric in enumerate(metrics)) / L_sum
        for j in range(len(data))
    ]
    return time_list, congestion_distance_ratio['R'].tolist()


def calculate_tcr(data, road_lengths):
    """
    计算交通拥堵指数 (TCR)。

    输入：
        data: 包含各路段 SPI 数据的 DataFrame。
        road_lengths: 路段长度列表。
    输出：
        tcr: 包含交通拥堵指数的 DataFrame，列名包括 '时间' 和 'TCR'。
    """
    metrics = ['路段1SPI', '路段2SPI', '路段3SPI', '路段4SPI', '路段5SPI', '路段6SPI', '路段7SPI']
    L_sum = sum(road_lengths)
    tcr = pd.DataFrame()
    time_list = []
    for datetime_str in data['时间']:
        time_list.append(time_trans(datetime_str))
    tcr['TCR'] = sum(road_lengths[i] * data[metric] for i, metric in enumerate(metrics)) / L_sum
    return time_list, tcr['TCR'].tolist()

# def get_road_and_all_metrics(direction, flow_data, speed_data, target_date):
#     """
#     获取选定方向的路段指标和全路段的综合指标，筛选指定日期的数据。
#
#     输入：
#         direction (str): 方向，可选 "upstream" 或 "downstream"。
#         flow_data (DataFrame): 包含流量数据的 DataFrame。
#         speed_data (DataFrame): 包含速度数据的 DataFrame。
#         target_date (str): 目标日期，格式为 "YYYY-MM-DD"。
#
#     输出：
#         result (dict): 包含选定路段的所有指标，每个指标为单独的列表。
#         all_metrics (dict): 包含全路段的综合指标，每个指标为单独的列表。
#     """
#     # 筛选指定日期的数据
#     flow_data = select_day_data(flow_data, target_date)
#     speed_data = select_day_data(speed_data, target_date)
#
#     # 获取道路参数
#     road_lengths, t95_times, free_flow_times = get_road_metrics(direction)
#
#     # 计算各路段的指标
#     flow_diff = calculate_flow_difference(flow_data)
#     service_level = calculate_service_level(flow_data)
#     average_speed = calculate_average_speed(speed_data)
#     spi = calculate_spi(speed_data)
#     congestion_duration = calculate_congestion_duration(spi)
#     tbi = calculate_tbi(speed_data, road_lengths, t95_times, free_flow_times)
#
#     # 准备结果
#     result = {
#         '路段流量差': flow_diff.iloc[:, 1:].values.tolist(),
#         '路段服务水平': service_level.iloc[:, 1:].values.tolist(),
#         '路段平均速度': average_speed.iloc[:, 1:].values.tolist(),
#         'SPI': spi.iloc[:, 1:].values.tolist(),
#         '拥堵持续时间': congestion_duration.iloc[:, 1:].values.tolist(),
#         'TBI': tbi.iloc[:, 1:].values.tolist(),
#     }
#
#     # 计算全路段指标
#     los_all = calculate_los_all(service_level, road_lengths)
#     congestion_distance_ratio = calculate_congestion_distance_ratio(spi, road_lengths)
#     tcr = calculate_tcr(spi, road_lengths)
#
#     # 准备全路段指标
#     all_metrics = {
#         'LoS_all': los_all['LoS_all'].tolist(),
#         '拥堵距离比率 (R)': congestion_distance_ratio['R'].tolist(),
#         '交通拥堵比率 (TCR)': tcr['TCR'].tolist(),
#     }
#
#     # 返回结果
#     return result, all_metrics
