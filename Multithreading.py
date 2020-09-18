import threading
from apscheduler.schedulers.blocking import BlockingScheduler
import cat_ceph_status
import cat_onenode


def thread1():
    job1=[cat_ceph_status.get_ceph_status,cat_ceph_status.get_osd_usage,cat_ceph_status.get_osd_status,
          cat_ceph_status.get_osd_latency,cat_ceph_status.get_pg_status,cat_ceph_status.get_mon_status,
          cat_ceph_status.get_ceph_disk_usage]
    for subjob in job1:
        # print(subjob)
        thread = threading.Thread(target=subjob)
        thread.start()

def thread2():
    job2 = [cat_onenode.disk_send_mgs, cat_onenode.mem_send_mgs, cat_onenode.load_send_mgs, cat_onenode.cpu_send_mgs]
    for subjob in job2:
        # print(subjob)
        thread = threading.Thread(target=subjob)
        thread.start()



def scheduler_jobs(spark):
    scheduler = BlockingScheduler()
    scheduler.add_job(func=spark, trigger="interval", seconds=5)
    scheduler.start()

if __name__ == '__main__':
    print("start")
    scheduler_jobs(thread1)
    scheduler_jobs(thread2)


