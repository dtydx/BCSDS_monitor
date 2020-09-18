# bcsds_monitor
- **alarm_sign.py：**获取本机基础信息，使用静态类获取包括IP地址，时间，主机名，全局警告标记等。
- **menu.py：**监控项菜单。
- **Multithreading.py：**负责创建多线程定时监控任务。
- **send_email.py：**负责监控告警邮件发送；
- **cat_ceph_status.py**：负责监控集群信息，包括集群健康状态，osd节点使用率，osd节点状态，osd延迟信息，pg状态，mon节点状态，集群磁盘使用率等等。
- **cat_onenode.py：**负责监控当前节点状态，包括系统磁盘状态，内存状态，系统负载，CPU状态等等。
