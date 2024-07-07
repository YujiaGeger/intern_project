import os
import sys
import tarfile
import gzip
import shutil
from datetime import datetime, timedelta
from pydlt import DltFileReader

def process_redirected_folder(base_folder):
    """
    遍历给定的文件夹，查找文件名包含 'PARK' 的 .dlt 文件。
    如果找到，将其内容转换为 .txt 文件并保存在相同位置。

    参数:
        base_folder (str): 要处理的基础文件夹路径。

    返回:
        bool: 如果找到并处理了至少一个 .dlt 文件，则返回 True，否则返回 False。
    """
    answer = False
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.endswith('.dlt') and 'PARK' in file:
                answer = True
                dlt_file_path = os.path.join(root, file)
                txt_file_path = os.path.splitext(dlt_file_path)[0] + '.txt'
                try:
                    with open(txt_file_path, 'w') as txt_file:
                        for msg in DltFileReader(dlt_file_path):
                            txt_file.write(f"{msg}\n")
                    print(f"成功转换文件: {dlt_file_path} 至 {txt_file_path}")
                except UnicodeDecodeError as e:
                    print(f"无法解码文件 {dlt_file_path}: {e}")
    return answer

def extract_closest_tar(history_folder, target_time):
    """
    在指定的历史文件夹中查找时间上最接近目标时间的 .tar 压缩文件（并且文件时间在目标时间之后），并解压该文件。

    参数:
        history_folder (str): 存放历史压缩包的文件夹路径。
        target_time (str): 目标时间，格式为 "YYYY/MM/DD - HH:MM:SS"。

    返回:
        str: 解压后的文件夹路径，如果没有找到合适的文件则返回 None。
    """
    closest_diff = float('inf')
    closest_file = None
    target_time = datetime.strptime(target_time, "%Y/%m/%d - %H:%M:%S")
    extracted_folder = None

    for root, _, files in os.walk(history_folder):
        for file in files:
            if file.endswith('.tar'):
                file = file.split(".tar")[0]
                try:
                    timestamp_str = '_'.join(file.split('_')[2:6])
                    file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H_%M_%S")
                    time_diff = abs((file_time - target_time).total_seconds())
                    if time_diff < closest_diff and file_time > target_time:
                        closest_diff = time_diff
                        closest_file = os.path.join(root, file)
                except ValueError:
                    print(f"文件名格式错误: {file}")

    if closest_file:
        closest_file = closest_file + ".tar"
        extracted_folder = os.path.splitext(closest_file)[0]
        with tarfile.open(closest_file, 'r') as tar:
            tar.extractall(path=extracted_folder)
        print(f"成功解压: {closest_file}")
    return extracted_folder

def check_files_in_extracted_folder(extracted_folder, target_time):
    """
    检查解压后的文件夹中是否有在目标时间之内、文件名包含 'PARK' 且包含 '.dlt' 但不包含 '.txt' 的文件。
    如果找到，将这些文件的后缀名改为 '.dlt'。

    参数:
        extracted_folder (str): 解压后的文件夹路径。
        target_time (str): 目标时间，格式为 "YYYY/MM/DD - HH:MM:SS"。

    返回:
        bool: 如果找到并处理了至少一个符合条件的文件，则返回 True，否则返回 False。
    """
    target_time = datetime.strptime(target_time, "%Y/%m/%d - %H:%M:%S")
    answer = False
    for root, _, files in os.walk(extracted_folder):
        for file in files:
            if 'PARK' in file and 'dlt' in file and 'txt' not in file:
                timestamp_str = file.split('_')[-1].split('.')[0]
                line_time = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
                if abs(line_time - target_time) <= timedelta(minutes=5):
                    print(f"找到文件: {os.path.join(root, file)}")
                    old_path = os.path.join(root, file)
                    new_path = old_path.replace('.finish.gz', '')
                    try:
                        with gzip.open(old_path, 'rb') as f_in:
                            with open(new_path, 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                    except FileExistsError:
                        print("文件已存在，将跳过")
                    answer = True
    return answer


def log_failures_to_txt(folder_directory, target_time):
    """
    遍历给定的文件夹，查找所有包含错误或失败信息的 .txt 文件，并将这些信息记录到 'failure.txt' 中。
    记录的错误信息应于目标时间前后五分钟之内。

    参数:
        folder_directory (str): 要检查的文件夹路径。
        target_time (str): 目标时间，格式为 "YYYY/MM/DD - HH:MM:SS"。

    返回:
        None
    """
    target_time = datetime.strptime(target_time, "%Y/%m/%d - %H:%M:%S")
    log_path = os.path.join(os.getcwd(), 'failure.txt')
    with open(log_path, 'w') as failure_log:
        for root, _, files in os.walk(folder_directory):
            for file in files:
                if file.endswith('.txt'):
                    txt_file_path = os.path.join(root, file)
                    with open(txt_file_path, 'r') as txt_file:
                        for line in txt_file:
                            if ('failure' in line or 'error' in line):
                                timestamp_str = line.split()[0] + ' ' + line.split()[1]
                                line_time = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S.%f")
                                #文件的五分钟吗，还是报错的五分钟（此处逻辑为报错的五分钟）
                                if abs(line_time - target_time) <= timedelta(minutes=5):
                                    failure_log.write(line)


#主要程序
def main(target_time):
    redirected_folder = os.path.join(os.getcwd(), '0416', 'log1' , 'log', 'redirected')
    history_folder = os.path.join(os.getcwd(), '0416', 'log1' ,'log', 'history')

    # 是否存在文件名包含Park的dlt文件，如果存在，转换为txt
    is_park_contained = process_redirected_folder(redirected_folder)
    
    if(is_park_contained):
        #遍历'txt'文件，寻找在错误时间范围内且包含'Failure'的信息，保存错误值到'failure.txt'
        log_failures_to_txt(redirected_folder, target_time)
        print("任务完成，退出脚本")
    else:
        # 解压指定错误时间发生之后的第一个压缩包
        extracted_folder = extract_closest_tar(history_folder, target_time)
        if(extracted_folder == None):
            print("无法找到解压之后文件地址")
        #遍历解压的文件夹，寻找是否有处在错误时间范围内，包含'PARK'和'.dlt'但不包含".txt'的文件，如果找到，将文件后缀改为.dlt
        is_file_contained = check_files_in_extracted_folder(extracted_folder, target_time)
        if(is_file_contained == False):
            print("任务完成，退出脚本")
        else:
            #将dlt文件变为txt文件
            process_redirected_folder(extracted_folder)
            #遍历'txt'文件，寻找在错误时间范围内且包含'Failure'的信息，保存错误值到'failure.txt'
            log_failures_to_txt(extracted_folder, target_time)
            print("任务完成，退出脚本")

#输入格式：python dlt_parser.py '2024/04/15 - 15:31:03'
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python dlt_parser.py '<error_time>'")
        print("例子: python dlt_parser.py '2024/04/15 - 15:31:03'")
        sys.exit(1)
    error_time_str = sys.argv[1]
    try:
        error_time = datetime.strptime(error_time_str, '%Y/%m/%d - %H:%M:%S')
    except ValueError:
        print("错误: 日期格式不正确。请使用 'YYYY/MM/DD - HH:MM:SS' 格式")
        sys.exit(1)
    main(error_time_str)
