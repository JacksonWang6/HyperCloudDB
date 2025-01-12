import re
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np
import matplotlib.font_manager as fm
import matplotlib

# 清理字体缓存
def parse_bandwith_usage(log_file_path, output_file):
    # font_path = '/home/ubuntu/HyperCloudDB/SimHei.ttf'  # 根据你的实际路径调整
    # prop = fm.FontProperties(fname=font_path)
    # plt.rcParams['font.sans-serif'] = ["SimHei"]
    # plt.rcParams['axes.unicode_minus'] = False   # 确保负号正常显示
    # plt.rcParams['figure.figsize'] = (10.0, 8.0)  # set default size of plots
    # plt.rcParams['image.interpolation'] = 'nearest'
    # plt.rcParams['image.cmap'] = 'gray'
    # 初始化数据存储列表
    timestamps = []
    read_bandwidth = []
    send_bandwidth = []
    disk_read_throughput = []
    disk_write_throughput = []
    net_total_bandwidth = []
    disk_total_bandwidth = []
    net_utilization = []  # 存储网卡带宽利用率
    disk_utilization = []  # 存储磁盘带宽利用率
    net_max_bandwidth = 300
    disk_max_bandwidth = 300
    first_timestamp = None

    # 正则表达式用于匹配每行的带宽数据
    net_bandwidth_pattern = r"NetDevice: (\S+),Read Bandwidth: (\S+) MB/s,Send Bandwidth: (\S+) MB/s"
    disk_bandwidth_pattern = r"Disk Device: (\S+),Read Throughput: (\S+) MB/sWrite Throughput: (\S+) MB/s"
    timestamp_pattern = r"MicroSecondsUp: (\d+)"

    with open(log_file_path, 'r') as file:
        for line in file:
            # 提取时间戳
            timestamp_match = re.search(timestamp_pattern, line)
            # if timestamp_match:
            #     timestamp_microseconds = int(timestamp_match.group(1))
            #     timestamp = datetime.datetime.utcfromtimestamp(timestamp_microseconds / 1e6)
            #     timestamps.append(timestamp)
            if timestamp_match:
                timestamp = int(timestamp_match.group(1))
                if first_timestamp is None:
                    first_timestamp = timestamp  # 记录第一个时间戳
                # 计算相对时间（秒）
                relative_timestamp = (timestamp - first_timestamp) / 1e6  # 微秒转秒
                timestamps.append(relative_timestamp)


            # 提取网卡带宽数据
            net_bandwidth_match = re.search(net_bandwidth_pattern, line)
            if net_bandwidth_match:
                read_bandwidth_value = float(net_bandwidth_match.group(2))
                send_bandwidth_value = float(net_bandwidth_match.group(3))
                read_bandwidth.append(read_bandwidth_value)
                send_bandwidth.append(send_bandwidth_value)
                
                net_total_bandwidth_value = read_bandwidth_value + send_bandwidth_value
                net_total_bandwidth.append(net_total_bandwidth_value)
                
                # 计算网卡带宽利用率
                net_utilization_value = (net_total_bandwidth_value / net_max_bandwidth) * 100
                net_utilization.append(net_utilization_value)
            
            # 提取磁盘带宽数据
            disk_bandwidth_match = re.search(disk_bandwidth_pattern, line)
            if disk_bandwidth_match:
                disk_read_value = float(disk_bandwidth_match.group(2))
                disk_write_value = float(disk_bandwidth_match.group(3))
                disk_read_throughput.append(disk_read_value)
                disk_write_throughput.append(disk_write_value)
                
                disk_total_bandwidth_value = disk_read_value + disk_write_value
                disk_total_bandwidth.append(disk_total_bandwidth_value)
                
                # 计算磁盘带宽利用率
                disk_utilization_value = (disk_total_bandwidth_value / disk_max_bandwidth) * 100
                disk_utilization.append(disk_utilization_value)

    # 转换时间戳为秒（如果需要的话）
    timestamps = [ts for ts in timestamps]  # 假设MicroSecondsUp是微秒，需要转换为秒
    # 将数据转换为DataFrame，以便于进一步分析
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Net Read Bandwidth (MB/s)': read_bandwidth,
        'Net Send Bandwidth (MB/s)': send_bandwidth,
        'Disk Read Throughput (MB/s)': disk_read_throughput,
        'Disk Write Throughput (MB/s)': disk_write_throughput,
        'Net Total Bandwidth (MB/s)': net_total_bandwidth,
        'Disk Total Bandwidth (MB/s)': disk_total_bandwidth,
        'Net Utilization (%)': net_utilization,
        'Disk Utilization (%)': disk_utilization
    })

    # 绘制折线图
    plt.figure(figsize=(12, 8), dpi=200)

    # 网卡带宽利用率
    plt.subplot(2, 1, 1)
    plt.plot(df['Timestamp'], df['Net Utilization (%)'], label='Net Utilization (%)', color='#4c9bff')
    # plt.axhline(y=100, color='purple', linestyle='--')  # 添加虚线，表示100%利用率
    plt.xlabel('Time(s)')
    plt.ylabel('Utilization (%)')


    ax = plt.gca()
    ax.get_yticklabels()[6].set_color('red')


    # 磁盘带宽利用率
    plt.subplot(2, 1, 2)
    plt.plot(df['Timestamp'], df['Disk Utilization (%)'], label='Disk Utilization (%)', color='#84c3b7')
    # plt.axhline(y=100, color='purple', linestyle='--')  # 添加虚线，表示100%利用率
    plt.xlabel('Time(s)')
    plt.ylabel('Utilization (%)')

    ax = plt.gca()
    ax.get_yticklabels()[4].set_color('red')
    # 调整布局，避免重叠
    plt.tight_layout()

    # 显示图表
    plt.show()
    plt.savefig(output_file)

# 解析带宽的函数，可以得到磁盘以及网卡
def parse_bandwith(log_file_path, output_file):
    # 初始化数据存储列表
    timestamps = []
    read_bandwidth = []
    send_bandwidth = []
    disk_read_throughput = []
    disk_write_throughput = []
    net_total_bandwidth = []  # 存储网卡总带宽数据
    disk_total_bandwidth = []  # 存储磁盘总带宽数据

    # 正则表达式用于匹配每行的带宽数据
    net_bandwidth_pattern = r"NetDevice: (\S+),Read Bandwidth: (\S+) MB/s,Send Bandwidth: (\S+) MB/s"
    disk_bandwidth_pattern = r"Disk Device: (\S+),Read Throughput: (\S+) MB/sWrite Throughput: (\S+) MB/s"
    timestamp_pattern = r"MicroSecondsUp: (\d+)"

    # 逐行解析日志文件
    with open(log_file_path, 'r') as file:
        for line in file:
            # 提取时间戳
            timestamp_match = re.search(timestamp_pattern, line)
            if timestamp_match:
                timestamp_microseconds = int(timestamp_match.group(1))
                timestamp = datetime.datetime.utcfromtimestamp(timestamp_microseconds / 1e6)
                timestamps.append(timestamp)
            
            # 提取网卡带宽数据
            net_bandwidth_match = re.search(net_bandwidth_pattern, line)
            if net_bandwidth_match:
                read_bandwidth_value = float(net_bandwidth_match.group(2))
                send_bandwidth_value = float(net_bandwidth_match.group(3))
                read_bandwidth.append(read_bandwidth_value)
                send_bandwidth.append(send_bandwidth_value)
                
                # 计算网卡总带宽 = 读带宽 + 发送带宽
                net_total_bandwidth_value = read_bandwidth_value + send_bandwidth_value
                net_total_bandwidth.append(net_total_bandwidth_value)
            
            # 提取磁盘带宽数据
            disk_bandwidth_match = re.search(disk_bandwidth_pattern, line)
            if disk_bandwidth_match:
                disk_read_value = float(disk_bandwidth_match.group(2))
                disk_write_value = float(disk_bandwidth_match.group(3))
                disk_read_throughput.append(disk_read_value)
                disk_write_throughput.append(disk_write_value)
                
                # 计算磁盘总带宽 = 读吞吐量 + 写吞吐量
                disk_total_bandwidth_value = disk_read_value + disk_write_value
                disk_total_bandwidth.append(disk_total_bandwidth_value)

    # 将数据转换为DataFrame，以便于进一步分析
    df = pd.DataFrame({
        'Timestamp': timestamps,
        'Net Read Bandwidth (MB/s)': read_bandwidth,
        'Net Send Bandwidth (MB/s)': send_bandwidth,
        'Disk Read Throughput (MB/s)': disk_read_throughput,
        'Disk Write Throughput (MB/s)': disk_write_throughput,
        'Net Total Bandwidth (MB/s)': net_total_bandwidth,
        'Disk Total Bandwidth (MB/s)': disk_total_bandwidth
    })

    # 绘制折线图
    plt.figure(figsize=(12, 8))

    # 网卡带宽
    plt.subplot(2, 1, 1)  # 2行1列的第一个子图
    plt.plot(df['Timestamp'], df['Net Read Bandwidth (MB/s)'], label='Net Read Bandwidth (MB/s)', color='orange')
    # plt.plot(df['Timestamp'], df['Net Send Bandwidth (MB/s)'], label='Net Send Bandwidth (MB/s)', color='cyan')
    plt.plot(df['Timestamp'], df['Net Total Bandwidth (MB/s)'], label='Net Total Bandwidth (MB/s)', color='purple', linestyle='dashed')

    # 设置网卡带宽子图标签
    plt.xlabel('Time')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('Network Bandwidth Over Time')
    plt.legend()

    # 磁盘带宽
    plt.subplot(2, 1, 2)  # 2行1列的第二个子图
    plt.plot(df['Timestamp'], df['Disk Read Throughput (MB/s)'], label='Disk Read Throughput (MB/s)', color='red')
    plt.plot(df['Timestamp'], df['Disk Write Throughput (MB/s)'], label='Disk Write Throughput (MB/s)', color='orange')
    plt.plot(df['Timestamp'], df['Disk Total Bandwidth (MB/s)'], label='Disk Total Bandwidth (MB/s)', color='purple', linestyle='dashed')

    # 设置磁盘带宽子图标签
    plt.xlabel('Time')
    plt.ylabel('Bandwidth (MB/s)')
    plt.title('Disk Bandwidth Over Time')
    plt.legend()

    # 调整布局，避免重叠
    plt.tight_layout()

    # 显示图表
    plt.show()
    plt.savefig(output_file)


# 解析Compaction时间
def parse_compaction(file1, file2):
    # 正则表达式，用来提取L{1} -> L{2} 和 cost 时间
    pattern = r'L\{(\d+)\} -> L\{(\d+)\}, cost \{([\d.]+)\} s'

    # 读取日志文件并提取数据
    def extract_costs(file_path):
        costs = []
        with open(file_path, 'r') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    # 提取 cost 时间
                    cost = float(match.group(3))
                    costs.append(cost)
        return costs

    # 提取两个文件的数据
    costs1 = extract_costs(file1)
    costs2 = extract_costs(file2)

    # 计算每个文件的分位数
    def get_percentiles(data):
        return {
            'Q1': np.percentile(data, 25),
            'median': np.percentile(data, 50),
            'Q3': np.percentile(data, 75),
            'min': np.min(data),
            'max': np.max(data)
        }

    percentiles1 = get_percentiles(costs1)
    percentiles2 = get_percentiles(costs2)

    # 绘制两个文件的箱型图对比
    plt.figure(figsize=(10, 6))

    # 绘制第一个文件的箱型图
    box1 = plt.boxplot(costs1, vert=True, patch_artist=True, 
                    boxprops=dict(facecolor='skyblue', color='blue'), 
                    medianprops=dict(color='red', linewidth=2), 
                    whiskerprops=dict(color='blue', linewidth=1.5), 
                    positions=[1], widths=0.5, showfliers=False)

    # 绘制第二个文件的箱型图
    box2 = plt.boxplot(costs2, vert=True, patch_artist=True, 
                    boxprops=dict(facecolor='lightgreen', color='green'), 
                    medianprops=dict(color='orange', linewidth=2), 
                    whiskerprops=dict(color='green', linewidth=1.5), 
                    positions=[2], widths=0.5, showfliers=False)

    # 标出分位数，放在箱体外面
    # plt.text(1, percentiles1['Q1'] - 0.05, f'Q1: {percentiles1["Q1"]:.3f}', ha='center', va='center', color='blue')
    # plt.text(1, percentiles1['median'] + 0.05, f'Median: {percentiles1["median"]:.3f}', ha='center', va='center', color='red')
    # plt.text(1, percentiles1['Q3'] + 0.05, f'Q3: {percentiles1["Q3"]:.3f}', ha='center', va='center', color='blue')

    # plt.text(2, percentiles2['Q1'] - 0.05, f'Q1: {percentiles2["Q1"]:.3f}', ha='center', va='center', color='green')
    # plt.text(2, percentiles2['median'] + 0.05, f'Median: {percentiles2["median"]:.3f}', ha='center', va='center', color='orange')
    # plt.text(2, percentiles2['Q3'] + 0.05, f'Q3: {percentiles2["Q3"]:.3f}', ha='center', va='center', color='green')

    # 设置标题和标签
    plt.title('Compaction Cost Distribution Comparison')
    plt.ylabel('Cost (seconds)')
    plt.xticks([1, 2], ['EBS', 'Hybrid'])
    plt.grid(True)

    # 显示图表
    plt.show()
    plt.savefig('compaction.jpg')

def parse_qps(file_path):
    # 读取日志文件并提取时间戳和写操作数
    def parse_log_file(file_path):
        timestamps = []
        write_ops = []

        with open(file_path, 'r') as file:
            lines = file.readlines()
            
            for line in lines:
                if 'MicroSecondsUp' in line:
                    # 提取时间戳
                    timestamp = int(line.split(":")[1].strip())
                    timestamps.append(timestamp)
                    
                if 'write ops' in line:
                    # 提取写操作数
                    try:
                        write_ops_count = int(line.split('write ops:')[1].split('op/s')[0].strip())
                        write_ops.append(write_ops_count / 1000)
                    except Exception:
                        pass

        return timestamps, write_ops

    # 解析日志文件
    timestamps, write_ops = parse_log_file(file_path)

    # 将时间戳从微秒转换为秒，并且与第一个时间戳对齐
    timestamps_in_seconds = [(ts - timestamps[0]) / 1e6 for ts in timestamps]

    # 创建图表，并设置图表大小
    plt.figure(figsize=(20, 6))  # 设置图表宽度为12，高度为6
    # 绘制图表
    plt.plot(timestamps_in_seconds, write_ops, marker='o', linestyle='-', color='b')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Write Operations (kilo op/s)')
    plt.title('Write Operations Over Time')
    plt.grid(True)
    plt.show()
    plt.savefig("qps.jpg")

def parse_multi_disk():
    # 用于解析带宽数据的正则表达式
    pattern_nvme = r"Disk Device: (nvme2n1p1|nvme2n1p2),Read Throughput: ([\d\.]+) MB/s, Write Throughput: ([\d\.]+) MB/s"
    pattern_time = r"MicroSecondsUp: (\d+)"

    # 存储时间和带宽数据
    timestamps = []
    nvme2n1p1_total_bandwidth = []
    nvme2n1p2_total_bandwidth = []
    first_timestamp = None

    # 读取日志文件
    with open('./a_my_log/ebs_bandwith_test/bg8_my_stat.log', 'r') as f:
        lines = f.readlines()

        for line in lines:
            time_match = re.search(pattern_time, line)
            if time_match:
                timestamp = int(time_match.group(1))
                if first_timestamp is None:
                    first_timestamp = timestamp  # 记录第一个时间戳
                # 计算相对时间（秒）
                relative_timestamp = (timestamp - first_timestamp) / 1e6  # 微秒转秒
                timestamps.append(relative_timestamp)

            # 查找nvme2n1p1和nvme2n1p2的带宽数据
            nvme_match = re.search(pattern_nvme, line)
            if nvme_match:
                device = nvme_match.group(1)
                read_bw = float(nvme_match.group(2))
                write_bw = float(nvme_match.group(3))
                
                total_bw = read_bw + write_bw  # 计算总带宽

                if device == 'nvme2n1p1':
                    nvme2n1p1_total_bandwidth.append(total_bw)
                elif device == 'nvme2n1p2':
                    nvme2n1p2_total_bandwidth.append(total_bw)

    # 转换时间戳为秒（如果需要的话）
    timestamps = [ts for ts in timestamps]  # 假设MicroSecondsUp是微秒，需要转换为秒

    # 绘图
    plt.figure(figsize=(10, 6), dpi=200)

    plt.plot(timestamps, nvme2n1p1_total_bandwidth, label="EBS SSTable R/W Bandwidth (MB/s)", color='#84c3b7')
    plt.plot(timestamps, nvme2n1p2_total_bandwidth, label="S3 SSTable R/W Bandwidth (MB/s)", color='#4c9bff')

    plt.xlabel('Time (s)')
    plt.ylabel('Total Bandwidth (MB/s)')
    plt.title('')
    plt.legend()
    # plt.grid(True)

    plt.show()
    plt.savefig("mulpt_disk.jpg")

if __name__ == '__main__':
    # parse_bandwith('./build/8000w.log/fillrandom_hyper1_my_stat.log', 'bandwith.jpg')
    # parse_compaction('./build/8000w.log/all_ebs.log', './build/8000w.log/hyper1.log')
    # parse_qps("./build/8000w.log/fillrandom_hyper1_my_stat.log")
    # parse_bandwith_usage('./a_my_log/8000w.log/fillrandom_hyper1_my_stat.log', 'bandwith.jpg')
    parse_multi_disk()
