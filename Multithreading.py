import threading
from apscheduler.schedulers.blocking import BlockingScheduler
import cat_ceph_status
import cat_onenode

class Multi_threading:
    def __init__(self):
        # self.tclose=1
        self.job1=[cat_ceph_status.get_ceph_status,cat_ceph_status.get_osd_usage,cat_ceph_status.get_osd_status,
              cat_ceph_status.get_osd_latency,cat_ceph_status.get_pg_status,cat_ceph_status.get_mon_status,
              cat_ceph_status.get_ceph_disk_usage,cat_onenode.disk_send_mgs, cat_onenode.mem_send_mgs,
              cat_onenode.load_send_mgs, cat_onenode.cpu_send_mgs,cat_ceph_status.get_crond_status,
                   cat_ceph_status.get_pool_usage]

    def thread1(self):
        for subjob in self.job1:
            print(subjob)
            thread = threading.Thread(target=subjob)
            thread.start()

    # def thread2(self):
    #     job2 = [cat_onenode.disk_send_mgs, cat_onenode.mem_send_mgs, cat_onenode.load_send_mgs, cat_onenode.cpu_send_mgs]
    #     for subjob in job2:
    #         # print(subjob)
    #         while self.tclose == 0:
    #         thread = threading.Thread(target=subjob)
    #         thread.start()
    #

    def scheduler_jobs(self,spark):
        scheduler = BlockingScheduler()
        scheduler.add_job(func=spark, trigger="interval", seconds=5)
        scheduler.start()

if __name__ == '__main__':
    print("start")
    task=Multi_threading()
    task.scheduler_jobs(task.thread1)
    # scheduler_jobs(thread2)
    # task.tclose=0


