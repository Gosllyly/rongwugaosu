import os
import time

import traci

from rongwugaosu_app.utils import reset_simulating


# 执行仿真操作
def simulate(args):
    # time.sleep(3)
    # 设置 SUMO 环境变量
    if "SUMO_HOME" not in os.environ:
        raise EnvironmentError("请设置 SUMO_HOME 环境变量，指向 SUMO 安装目录。")

    # SUMO 执行路径
    sumo_binary = os.path.join(os.environ["SUMO_HOME"], "bin", "sumo")

    # 仿真配置文件路径
    # 获取当前文件目录的绝对路径
    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    # 设置 sumo 配置文件的绝对路径
    config_file = current_dir_path + "/sumo/osm.sumocfg"

    # 解析k-v 参数
    step = args.get("step")

    # 根据 args 传进的参数，再去修改 sumo 启动需要的路由文件 sumo/routes.rou.xml todo
    # 可以定义一个文件模板，每次修改模板文件中的占位符，生成新的文件作为 sumo 启动所需的文件

    # 启动 SUMO
    traci.start([sumo_binary, "-c", config_file])

    # 仿真循环
    # SUMO 的仿真是基于时间步（step）的，每步通常对应 1 秒（默认情况下），但也可以调整
    # 如果需要模拟 1 小时的交通流量，仿真步数就是 3600 步
    cur_step = 0
    print(f"仿真步数：{step}")
    while step < step:  # 运行 100 步
        traci.simulationStep()  # 执行仿真一步
        cur_step += 1

    # 停止仿真
    traci.close()
    print("仿真完成！")
    # 仿真状态复位
    reset_simulating()



