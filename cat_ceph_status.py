import subprocess
try:
    import simplejson as json
except:
    import json
from alarm_sign import alarm_sign
from sendemail import Email
from sendemail import Config

#设置email属性
email = Email(Config.MAILSERVER, Config.MAILPORT, Config.SENDER, Config.EPASS, Config.RECEIVER)

##获取集群状态 HEALTH_ERR、HEALTH_WARN、HEALTH_OK
def get_ceph_status():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph -s -f json", shell=True, stdout=subprocess.PIPE)
    j_data = json.loads(p.stdout.read())
    status = j_data.get('health').get('overall_status')
    run_events = "集群状态为{}".format(status)
    if status == 'HEALTH_OK':
        ceph_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,"None")
        return ceph_status
    else:
        q = subprocess.Popen("/var/lib/ceph/bin/ceph health", shell=True, stdout=subprocess.PIPE)
        problem = q.stdout.readlines()
        hint_content=problem[0].decode()
        ceph_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, hint_content)
        email.txt_email('集群状态出现异常', ceph_status)
        return ceph_status

##检查osd使用率
def get_osd_usage():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph osd df |awk '{print $1,$8;}'", shell=True, stdout=subprocess.PIPE)
    osds = p.stdout.readlines()
    dicts = {}
    error=''
    for o in osds:
        o=o.decode()
        array = o.strip().split(' ')
        try:
            id = int(array[0])
            dicts[id] = array[1]+'%'
            if int(array[1])>60:
                error+=str(id)+':'+dicts[id]+'\n'
        except ValueError:
            pass
    # print(dicts)
    # j_data = json.dumps(dicts, indent=4)
    # return j_data
    run_events=''
    for i,j in dicts.items():
        run_events += "osd{}节点使用率为{};\n".format(i,j)
    if error=='':
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{}提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, "None")
        return osd_usage
    else:
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, error)
        email.txt_email('osd节点使用率使用率过高', osd_usage)
        return osd_usage

##获取osd状态 0表示没有down的osd, 1表示有down
def get_osd_status():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph osd stat -f json", shell=True, stdout=subprocess.PIPE)
    data = json.loads(p.stdout.read())
    if data.get('num_osds') == data.get('num_up_osds') == data.get("num_in_osds"):
        run_events = "osd节点状态正常，在线数为{}".format(data.get('num_up_osds'))
        osd_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,"None")
        return osd_status
    else:
        run_events = "osd节点数为{}，down机数为{},".format(data.get('num_osds'),data.get('num_down_osds'))
        hint_content='存在osd节点down机'
        osd_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,hint_content)
        email.txt_email('存在osd节点down机', osd_status)
        return osd_status


##获取pg状态 0表示 active+clean, 1表示有问题
def get_pg_status():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph pg stat -f json", shell=True, stdout=subprocess.PIPE)
    data = json.loads(p.stdout.read())
    pg_name=data.get("num_pg_by_state")
    run_events = "放置组PG状态为{}".format(pg_name[0]["name"])
    if len(data.get("num_pg_by_state")) > 1:
        hint_content='放置组PG存在故障'
        pg_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, hint_content)
        email.txt_email('pg状态异常', pg_status)
        return pg_status
    else:
        pg_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,"None")
        return pg_status

def dict_Avg( Dict ) :#去字典值的平均数
    L = len( Dict )
    S = sum( Dict.values() )
    A = S / L
    return A

##获取osd延迟信息
def get_osd_latency():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph osd perf |awk '{print $1,$3}'", shell=True, stdout=subprocess.PIPE)
    osds = p.stdout.readlines()
    dicts = {}
    run_events=""
    hint_content=""
    for o in osds:
        o = o.decode()
        array = o.strip().split(" ")
        try:
            id = int(array[0])
            dicts[id] = int(array[1])
        except ValueError:
            pass
    avr_osd=dict_Avg(dicts)
    for i,j in dicts.items():
        run_events += "osd{}节点的延迟为{};\n".format(i,j)
        if j-avr_osd>50:
            hint_content += "osd{}节点的延迟较高建议踢除；\n".format(i)
    if hint_content == '':
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, "None")
        return osd_usage
    else:
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, hint_content)
        email.txt_email('存在osd节点延迟过高', osd_usage)
        return osd_usage

##检测mon状态
def get_mon_status():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph mon_status", shell=True, stdout=subprocess.PIPE)
    # usage = p.stdout.read()
    j_data = json.loads(p.stdout.read())
    name= j_data.get('name')
    rank=j_data.get('rank')
    status = j_data.get('state')
    # json_usage = json.loads(usage)
    run_events = "mon节点为{}，角色为{}".format(name,status)
    if status=='leader' or status=='peon':
        osd_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, alarm_sign.hint_content)
        return osd_status
    else:
        hint_content="Mon节点异常"
        osd_status = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, hint_content)
        email.txt_email('Mon节点异常', osd_status)
        return osd_status



##ceph集群所有磁盘使用率
def get_ceph_disk_usage():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph df -f json", shell=True, stdout=subprocess.PIPE)
    j_data = json.loads(p.stdout.read())
    pools = j_data.get('pools')
    run_events=''
    hint_content=''
    for item in pools:
        name=item.get('name')
        used=item.get('stats').get('bytes_used')
        percent_used=item.get('stats').get('percent_used')
        max_avail=item.get('stats').get('max_avail')
        run_events += "磁盘{}总容量为{}，已使用{}，使用率为{}%;\n".format(name,max_avail,used,percent_used)
        if int(percent_used)>50:
            hint_content += "磁盘{}使用率过高;\n".format(name)
    if hint_content != '':
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:\n{}提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,hint_content )
        email.txt_email('存在磁盘使用率过高', osd_usage)
        return osd_usage
    else:
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:\n{}提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, "None")
        return osd_usage

def get_crond_status():
    p1 = subprocess.Popen("ps aux|grep crond", shell=True, stdout=subprocess.PIPE)
    crond = p1.stdout.readlines()
    p2 = subprocess.Popen("ps aux|grep sdsom-rcm", shell=True, stdout=subprocess.PIPE)
    sdsom_rcm = p2.stdout.readlines()
    p3 = subprocess.Popen("ps aux|grep mysql", shell=True, stdout=subprocess.PIPE)
    mysql = p3.stdout.readlines()
    hint_content=''
    if len(crond)>=2 and len(sdsom_rcm)>=2 and len(mysql)>=2:
        run_events = "BC-SDS管理系统运行正常"
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, "None")
        return osd_usage
    else:
        run_events = "BC-SDS管理系统存在故障"
        if len(crond)<2:
            hint_content+='crond进程运行异常;'
        elif len(sdsom_rcm)<2:
            hint_content+='sdsom_rcm进程运行异常;'
        elif len(mysql)<2:
            hint_content += 'mysql进程运行异常;'
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:{};\n提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events,hint_content)
        email.txt_email('管理系统异常', osd_usage)
        return osd_usage

def get_pool_usage():
    p = subprocess.Popen("/var/lib/ceph/bin/ceph osd pool stats -f json", shell=True, stdout=subprocess.PIPE)
    j_data = json.loads(p.stdout.read())
    run_events=""
    hint_content=""
    for data in j_data:
        pool_name=data.get('pool_name')
        state=data.get('status').get('state')
        run_events += "资源池{}状态为{}".format(pool_name,state)
        try:
            client_io_rate=date.get('client_io_rate')
            run_events += ",client_io为{}%;\n".format(client_io_rate)
        except:
            run_events += ";\n"
        if state!=" health ":
            hint_content+="资源池{}状态异常；\n".format(pool_name)
    if hint_content != "":
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:\n{}提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, hint_content)
        email.txt_email('资源池异常', osd_usage)
        return osd_usage
    else:
        osd_usage = "获取时间:{};\n内网地址:{};\n主机名称:{};\n详细信息:\n{}提示内容:{}.".format(
            alarm_sign.get_date_time, alarm_sign.inside_net, alarm_sign.host_name, run_events, "None")
        return osd_usage




    # json_usage = json.loads(usage)
    # return json_usage


