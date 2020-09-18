import time,socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

class alarm_sign:
    # IP地址
    get_date = time.strftime("%Y-%m-%d", time.localtime())
    get_date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    inside_net = get_host_ip()
    host_name = socket.gethostname()# 主机名
    hint_content = "None"  # 发生事件
