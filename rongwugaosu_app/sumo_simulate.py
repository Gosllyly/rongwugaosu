import os
import time

import traci
from traci import FatalTraCIError

from rongwugaosu_app.utils import reset_simulating
import xml.etree.ElementTree as ET


# 执行仿真操作
def simulate(args):
    try:
        # 解析k-v 参数
        step = args.get("step")  # 仿真的时间，单位是秒
        roadName = args.get('roadName')  # 路段名称
        speedLimit = args.get('speedLimit')  # 路段限速
        direction = args.get('direction')  # 运行方向,0代表上行，1代表下行
        amplitude = args.get('amplitude')  # 超速幅度
        trafficDem = args.get('trafficDem')  # 交通需求
        # type = args.get('type')  # 类型，代表是自定义参数设置的仿真，1代表是典型场景的仿真
        # selection = args.get('selection')  # 时段选择，传0代表从0点到1点，传1代表从1点到2点，以此类推
        direction_dict = {0: "S", 1: "X"}
        amplitude_dict = {10: 3.611, 20: 3.889}
        # 仿真配置文件路径
        # 获取当前文件目录的绝对路径
        current_dir_path = os.path.dirname(os.path.abspath(__file__))
        # 修改xml文件
        xml_file = current_dir_path + "/sumo/routes.rou.xml"
        # 解析 XML 文件
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # 遍历所有 vType 元素
        for vtype in root.findall('vType'):
            # 检查元素的 id 属性
            if vtype.get('id') == 'passenger':
                max_speed = str(round(speedLimit / amplitude_dict[amplitude], 2))
                vtype.set('maxSpeed', max_speed)
        for flow in root.findall('flow'):
            # 检查元素的 id 属性
            if flow.get('type') == 'passenger':
                flow.set('id', f"{direction_dict[direction]}{roadName}")
                flow.set('route', f"{direction_dict[direction]}{roadName}")
                flow.set('end', str(step))
                flow.set('probability', str(round(trafficDem / 3600, 4)))
                # 将修改后的 XML 写回文件
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        # 可以定义一个文件模板，每次修改模板文件中的占位符，生成新的文件作为 sumo 启动所需的文件

        # time.sleep(3)
        # 设置 SUMO 环境变量
        if "SUMO_HOME" not in os.environ:
            raise EnvironmentError("请设置 SUMO_HOME 环境变量，指向 SUMO 安装目录。")

        # SUMO 执行路径
        sumo_binary = os.path.join(os.environ["SUMO_HOME"], "bin", "sumo")

        # 设置 sumo 配置文件的绝对路径
        config_file = current_dir_path + "/sumo/osm.sumocfg"

        # 启动 SUMO
        traci.start([sumo_binary, "-c", config_file])

        # 仿真循环
        # SUMO 的仿真是基于时间步（step）的，每步通常对应 1 秒（默认情况下），但也可以调整
        # 如果需要模拟 1 小时的交通流量，仿真步数就是 3600 步
        cur_step = 0
        print(f"仿真步数：{step}")
        while cur_step < step:  # 运行 100 步
            traci.simulationStep()  # 执行仿真一步
            cur_step += 1

        # 停止仿真
        traci.close()
        print("仿真完成！")
    except Exception as e:
        print(f"FatalTraCIError......{e}")
    finally:
        # 仿真状态复位
        reset_simulating()
