import sched
import time


class Task(object):
    def __init__(self, delay, action, *argument):
        super(Task, self).__init__()

        self.delay = delay  # 执行周期，以秒为单位
        self.action = action  # 回调方法
        self.argument = argument  # 回调方法参数

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def start(self):
        self.action(*self.argument)
        self.scheduler.enter(self.delay, 1, self.start, ())


class Task_Queue(object):
    def __init__(self):
        super(Task_Queue, self).__init__()

        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.tasks = []

    def push(self, task):
        self.tasks.append(task)

    def start(self):
        for task in self.tasks:
            task.set_scheduler(self.scheduler)
            task.start()
        self.scheduler.run()


if __name__ == '__main__':
    def _print_add(a, b):
        print(a + b)

    queue = Task_Queue()
    task = Task(2, _print_add, 1, 2)
    queue.push(task)
    queue.start()
