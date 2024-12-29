
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import yaml
from .STAEformer import *



class StandardScaler:
    def __init__(self, mean=None, std=None):
        self.mean = mean
        self.std = std

    def transform(self, data):
        return (data - self.mean) / self.std

    def inverse_transform(self, data):
        return (data * self.std) + self.mean


class STAEformerPredictor:
    def __init__(self, dataset, data_index, predict_time_frame=288):

        self.cfg = self.load_config(dataset)
        self.dataset = dataset
        self.data_start_index = data_index
        self.data_end_index = self.data_start_index + 24
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = StandardScaler(mean=self.cfg['data_mean'], std=self.cfg['data_std'])
        self.model = self.load_model(self.cfg["model_args"])
        self.data = self.load_data()
        self.num = self.data.shape[1]
        self.predict_time_frame = predict_time_frame

    def load_config(self, dataset):
        with open("./STAEformer_last.yaml", "r") as f:
            cfg = yaml.safe_load(f)
        return cfg[dataset]

    def load_data(self):
        data_temp = np.load(f"..\\data\\{self.dataset}\\combined_data.npz")['combined_data']
        data_temp[:, :, 2] -= 1  # Adjusting data as per your requirement
        features = [0]
        if self.cfg['time_of_day']:
            features.append(3)
        if self.cfg['day_of_week']:
            features.append(1)
        if self.cfg['day_of_month']:
            features.append(2)
        return data_temp[..., features]

    def load_model(self, model_args):
        model = STAEformer(**model_args).to(self.device)
        model.load_state_dict(torch.load(f'..\\saved_models\\STAEformer-{self.dataset}.pt'))
        model.eval()
        return model

    def predict_long(self):
        input_data = self.data[self.data_start_index:self.data_end_index, :, :]
        input_data[..., 0] = self.scaler.transform(input_data[:, :, 0])

        out_np = np.zeros((self.num, self.predict_time_frame))

        for t in range(self.predict_time_frame):
            input_tensor = torch.from_numpy(input_data).float().unsqueeze(dim=0).to(self.device)
            with torch.no_grad():
                out = self.model(input_tensor).cpu().numpy()
            new_input = out[:, 0, :, :].squeeze()
            out_np[:, t] = new_input
            input_data = np.roll(input_data, shift=-1, axis=0)
            input_data[-1, :, 0] = new_input
            input_data[-1, :, 1:] = self.data[self.data_end_index + t, :, 1:]

        return self.scaler.inverse_transform(out_np)

    def predict_short(self):
        input_data = self.data[self.data_start_index:self.data_end_index, :, :]
        input_data[..., 0] = self.scaler.transform(input_data[:, :, 0])

        input_tensor = torch.from_numpy(input_data).float().unsqueeze(dim=0).to(self.device)
        with torch.no_grad():
            out = self.model(input_tensor).cpu().numpy()
        squeezed_out = out.squeeze()
        return self.scaler.inverse_transform(squeezed_out.T)

    def save_predictions(self, predictions, output_file):
        output_df = pd.DataFrame(predictions)
        output_df.to_csv(output_file, index=False)


def parse_date(date_str):
    """自定义解析日期的函数，格式为 YYYY-MM-DD HH:MM:SS"""
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def predict_flow(date, roadName, direction, type, startTime):
    time_index = int(
        (parse_date(date_process(date, startTime)) - parse_date('2023-01-01 00:00:00')).total_seconds() / 300 - 24)
    time_list = time_list_process("00:00", time_index, 5)
    predictor_flow = STAEformerPredictor(f'FLOW_{direction}', time_index)
    # start_time = time.time()
    if type == 0:
        predictions_flow = predictor_flow.predict_short()
    else:
        predictions_flow = predictor_flow.predict_long()
    # print("Flow prediction running time:", time.time() - start_time)
    return time_list, list(predictions_flow[roadName])


# 预测速度的主要逻辑
def predict_speed(date, roadName, direction, type, startTime):
    time_index = int(
        (parse_date(date_process(date, startTime)) - parse_date('2023-01-01 00:00:00')).total_seconds() / 300 - 24)
    time_list = time_list_process("00:00", time_index, 5)
    if direction == 0:
        if date >= parse_date('2024-01-01'):
            time_index -= 96480
        else:
            time_index -= 69960

    predictor_speed = STAEformerPredictor(f'SPEED_{direction}', time_index)
    # start_time = time.time()
    if type == 0:
        predictions_speed = predictor_speed.predict_short()
    else:
        predictions_speed = predictor_speed.predict_long()
    # print("Speed prediction running time:", time.time() - start_time)
    return time_list, list(predictions_speed[roadName])


def time_list_process(original_time_str, time_index, delta):
    time_list = []
    new_time_str = original_time_str
    time_list.append(new_time_str)
    # 将字符串转换为 datetime 对象
    # 在此例中，我们只关心时间部分，因此日期可以使用任意有效的日期
    for i in range(time_index):
        original_datetime = datetime.strptime(new_time_str, "%H:%M")
        # 增加五分钟
        new_datetime = original_datetime + timedelta(minutes=delta)
        # 将 datetime 对象格式化为字符串
        new_time_str = new_datetime.strftime("%H:%M")
        time_list.append(new_time_str)
    return time_list


def date_process(date, startTime):
    # 将字符串转换为 datetime 对象
    original_datetime = datetime.strptime(date, "%Y-%m-%d")
    # 增加两个小时
    new_datetime = original_datetime + timedelta(hours=startTime)
    # 将 datetime 对象格式化为字符串
    return new_datetime.strftime("%Y-%m-%d %H:%M:%S")


# 主函数:输出预测的流量和速度（列表）
def main(direction, date, time_type, section):
    """
    :param direction: Upward and downward direction,'UP' or 'DOWN'
    :param date: Date in 'YYYY-MM-DD HH:MM:SS' format
    :param time_type: 'short_term' or 'long_term'
    :param section: section name --> str
    :return prediction of flow and speed --> list,list
    """
    section_dict = {'UP': {'k628': 0, 'k633': 1, 'k660': 2, 'k664': 3, 'k679': 4, 'k681': 5, 'k682': 6},
                    'DOWN': {'k682': 0, 'k679': 1, 'k664': 2, 'k660': 3, 'k633': 4, 'k629': 5, 'k628': 6}}

    args = {
        'direction': direction,
        'date': date,
        'time_type': time_type,
        'section_id': section_dict[direction][section]
    }
    return predict_flow(args), predict_speed(args)

# if __name__ == '__main__':
#     flow, speed = main('DOWN', parse_date('2024-01-01 02:10:00'), 'long_term', 'k628')
# """
# 输入:
#     运行方向："UP" 或 "DOWN";
#     时间：'YYYY-MM-DD HH:MM:SS'（字符串）;
#         日期 + 开始时间-->YYYY-MM-DD HH:MM:SS
#     预测类型："long_term" 或 "short_term";
#     路段名称："kxxx"(字符串).
# 输出：如果是长时预测，输出为len=288的列表；如果是短时预测，输出为len=12的列表
#
# """
