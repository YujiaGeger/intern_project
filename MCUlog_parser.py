import os
import re
import sys
from datetime import datetime, timedelta
def abc(v):
    return v + 30
def read_logs(mcu_log_path, error_time):
    """
    读取日志文件并提取在指定时间之前的ErrorManager错误日志。

    参数:
    mcu_log_path (str): MCU日志文件的路径。
    error_time (datetime): 错误时间，提取在此时间之前的错误日志。

    返回:
    list: 包含所有在指定时间之前的ErrorManager错误日志的列表。
    """
    car_time_re = re.compile(r'g_nCarTime\s+=\s+(\d+)')
    error_manager_re = re.compile(r'ErrorManager\s+:\s+(.*)')
    error_log_entries = []
    inside_range = False
    for root, _, files in os.walk(mcu_log_path):
        for file in files:
            if file.endswith('.log'):
                with open(os.path.join(root, file), 'r') as log_file:
                    lines = log_file.readlines()
                    for line in lines:
                        car_time_match = car_time_re.search(line)
                        if car_time_match:
                            car_time = float(car_time_match.group(1)) / 1000
                            car_time_dt = datetime.fromtimestamp(car_time)
                            if abs(car_time_dt - error_time) <= timedelta(minutes=5):
                                inside_range = True
                    for line in lines:
                        if(inside_range):
                            if 'ErrorManager' in line:
                                error_manager_match = error_manager_re.search(line)
                                if error_manager_match:
                                    error_log_entries.append(error_manager_match.group(1))
    return error_log_entries

def write_error_log(error_log_entries, output_file):
    """
    将错误日志条目写入指定的输出文件。

    参数:
    error_log_entries (list): 错误日志条目列表。
    output_file (str): 输出文件路径。
    """
    with open(output_file, 'w') as log_file:
        for entry in error_log_entries:
            log_file.write(entry + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python MCUlog_parser.py '<error_time>'")
        print("例子: python MCUlog_parser.py '2024/04/15 - 15:31:03'")
        sys.exit(1)
    error_time_str = sys.argv[1]
    try:
        error_time = datetime.strptime(error_time_str, '%Y/%m/%d - %H:%M:%S')
    except ValueError:
        print("错误: 日期格式不正确。请使用 'YYYY/MM/DD - HH:MM:SS' 格式")
        sys.exit(1)
    
    mcu_log_path = os.path.join('0416', 'log1', 'log', 'MCUlog', 'running')
    output_file = 'error_messages.log'
    
    error_log_entries = read_logs(mcu_log_path, error_time)
    
    if error_log_entries:
        write_error_log(error_log_entries, output_file)
        print(f"错误日志已创建: {output_file}")
    else:
        print("在指定的错误时间之内没有找到ErrorManager条目。")
