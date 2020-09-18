import os
from collections import namedtuple
from collections import OrderedDict
from alarm_sign import alarm_sign
from sendemail import Email
from sendemail import Config

# 获取磁盘信息
disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
usage_ntuple = namedtuple('usage', 'total used free percent')
#设置email属性
email = Email(Config.MAILSERVER, Config.MAILPORT, Config.SENDER, Config.EPASS, Config.RECEIVER)

# 获取所有磁盘设备,返回所有已挂载的分区作为一个名称元组,如果全部== False，则仅返回物理分区。
def disk_partitions(all=False):
    phydevs = []
    f = open("/proc/filesystems", "r")
    for line in f:
        if not line.startswith('none'):
            phydevs.append(line.strip())
        retlist = []
        f = open('/etc/mtab', "r")
        for line in f:
            if not all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            ntuple = disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
        print('disk_partitions:',retlist)
        return retlist


# 统计磁盘使用情况,返回与路径关联的磁盘使用情况
def disk_state(path):
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    return usage_ntuple(round(total / 1024 / 1024 / 1024, 3), round(used / 1024 / 1024 / 1024, 3),
                        round(free / 1024 / 1024 / 1024, 3), round(percent, 3))


#内存信息,以字典形式返回/proc/meminfo中的信息
def get_meminfo():
    meminfo = OrderedDict()
    with open('/proc/meminfo') as f:
        for line in f:
            meminfo[line.split(':')[0]] = line.split(':')[1].strip()
    return meminfo

# 负载信息
def get_load():
    f = open("/proc/loadavg")
    loadstate = f.read().split()
    return loadstate


# CPU信息
def get_cpu_use():
    last_worktime = 0
    last_idletime = 0
    f = open("/proc/stat", "r")
    line = ""
    while not "cpu " in line:
        line = f.readline()
    f.close()
    spl = line.split(" ")
    worktime = int(spl[2]) + int(spl[3]) + int(spl[4])
    idletime = int(spl[5])
    dworktime = (worktime - last_worktime)
    didletime = (idletime - last_idletime)
    rate = float(dworktime) / (didletime + dworktime)
    cpu_t = rate * 100
    last_worktime = worktime
    last_idletime = idletime
    if (last_worktime == 0):
        return 0
    return cpu_t

# 磁盘
def disk_send_mgs():
    disk_paths = ['/', '/boot']
    for disk_path in disk_paths:
        disk_new_state = disk_state(disk_path)
        disk_percent = float(disk_state(disk_path)[3])
        # print(disk_new_state)
        # print(disk_percent)
        run_events = "目录{}使用率为{}%".format(disk_path, disk_new_state[3])
        disk_send_state = "获取时间:{};\n内网地址:{};\n主机名称:{};\n发生事件:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, alarm_sign.hint_content)
            #send_text(disk_send_state)
        if disk_percent >= 60:
            email.txt_email('系统磁盘出现异常',disk_send_state)
        return disk_send_state


# 内存
def mem_send_mgs():
    get_run_meminfo = get_meminfo()  # 数据转换为list
    memtotal = format(get_run_meminfo['MemTotal'])
    memtotal = float(memtotal.split()[0])
    memfree = format(get_run_meminfo['MemFree'])
    memfree = float(memfree.split()[0])
    memswap = format(get_run_meminfo['SwapTotal'])
    memswap = float(memswap.split()[0])
    memswapfree = format(get_run_meminfo['SwapFree'])
    memswapfree = float(memswapfree.split()[0])
    mem_percent = round(((memtotal - memfree) / memtotal) * 100, 1)
    memswap_percent = round(((memswap - memswapfree) / memswap) * 100, 1)
    run_events = "内存使用率超过{}%".format(mem_percent)
    run_events += '\n'+"交换内存使用率超过{}%".format(memswap_percent)
    memswap_send_state = "获取时间:{};\n内网地址:{};\n主机名称:{};\n发生事件:{};\n提示内容:{}.".format(
        alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, alarm_sign.hint_content)
        # send_text(memswap_send_state)
    if memswap_percent >60 or mem_percent >60:
        email.txt_email('系统内存出现异常',memswap_send_state)
    return memswap_send_state


# 负载
def load_send_mgs():
    loadstate = get_load()
    loadstate1 = loadstate[0]
    loadstate15 = float(loadstate[2])
    run_events = "系统负载过高{}%".format(loadstate15)
    load_send_state = "获取时间:{};\n内网地址:{};\n主机名称:{};\n发生事件:{};\n提示内容:{}.".format(
        alarm_sign.get_date_time,alarm_sign.inside_net,alarm_sign.host_name,run_events,alarm_sign.hint_content)
    #send_text(load_send_state)
    if loadstate15 >= 5:
        email.txt_email('系统负载出现异常',load_send_state)
    #print ('负载：', load_send_state)
    return load_send_state


# CPU
def cpu_send_mgs():
    cpuuse_percent = round(get_cpu_use(), 3)

    run_events = "CPU使用率为{}%".format(cpuuse_percent)
    cpu_send_state = "获取时间:{};\n内网地址:{};\n主机名称:{};\n发生事件:{};\n提示内容:{}.".format(
        alarm_sign.get_date_time,alarm_sign.inside_net,alarm_sign.host_name,run_events, alarm_sign.hint_content)
     #send_text(cpu_send_state)
    if cpuuse_percent > 60:
        email.txt_email('CPU出现异常',cpu_send_state)
    #print('CPU：',cpu_send_state)
    return cpu_send_state



