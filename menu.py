import cat_ceph_status
import cat_onenode

if __name__ == '__main__':

    print("1.获取集群状态 HEALTH_ERR、HEALTH_WARN、HEALTH_OK")
    print("2:检查osd使用率")
    print("3.获取osd状态 0表示没有down的osd, 1表示有down")
    print("4.获取osd延迟信息")
    print("5.获取pg状态 0表示 active+clean, 1表示有问题")
    print("6.获取mon 状态")
    print("7.ceph集群所有磁盘使用率")
    print("8.获取当前节点磁盘状态")
    print("9.获取当前节点内存状态")
    print("10.获取当前系统负载")
    print("11.获取当前节点CPU状态")
    print("EXIT:输入q退出")
    inputs = ''
    while(inputs !='q'):
        inputs = input()
        if inputs == '1':##获取集群状态 HEALTH_ERR、HEALTH_WARN、HEALTH_OK
            print(cat_ceph_status.get_ceph_status())
        if inputs == '2':##检查osd使用率
            print(cat_ceph_status.get_osd_usage())
        if inputs == '3':##获取osd状态 0表示没有down的osd, 1表示有down
            print(cat_ceph_status.get_osd_status())
        if inputs == '4':##获取osd延迟信息
            print(cat_ceph_status.get_osd_latency())
        if inputs == '5':##获取pg状态 0表示 active+clean, 1表示有问题
            print(cat_ceph_status.get_pg_status())
        if inputs == '6':##mon 状态
            print(cat_ceph_status.get_mon_status())
        if inputs == '7':##ceph集群所有磁盘使用率
            print(cat_ceph_status.get_ceph_disk_usage())
        if inputs == '8':
            print(cat_onenode.disk_send_mgs())
        if inputs == '9':
            print(cat_onenode.mem_send_mgs())
        if inputs == '10':
            print(cat_onenode.load_send_mgs())
        if inputs == '11':
            print(cat_onenode.cpu_send_mgs())




