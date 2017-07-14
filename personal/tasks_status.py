import ee
ee.Initialize()

print "Tasks running", len([task for task in ee.data.getTaskList() if task['state'] == 'RUNNING'])
tasks = ee.data.getTaskList()
# print type(tasks)
print tasks

if len ( tasks ) == 0:
    print "no tasks"

# print tasks[0]['id'],len( tasks[0]['id'])

# try:
#     result = ee.data.getTaskStatus(task.id)[0]
# except:
#     print "Exception - task not found"
# result = ee.data.getTaskStatus(tasks[0])
# print result
#state = result['state']
# if state in ['READY', 'RUNNING']:#
#     print 'Exporting %s ...' %(state)#
# elif state in ['COMPLETED']:
#     #All GOOD
#     print 'Done %s ...' %(state)
# else:
#     print 'Error  %s ...' %(state)

print ee.batch.Task.list()

def get_tasks():
    return ee.batch.Task.list ()

all_tasks = get_tasks ()
tasks_running = [task for task in all_tasks if task.config['state'] in (u'RUNNING' , u'UNSUBMITTED' , u'READY')]
print tasks_running
for task_running in  tasks_running:
    print str(task_running).split(":")[1].split()[0].strip()

tasks_completed = [task for task in all_tasks if task.config['state'] in (u'COMPLETED')]
print tasks_completed

tasks_cancelled = [task for task in all_tasks if task.config['state'] in (u'CANCELLED')]
print tasks_cancelled

# statuses = ee.data.getTaskStatus(tasks)
# print statuses
#
# for status in statuses:
#     if status['state'] == 'FAILED':
#         task_id = status['id']
#         filename = tasks[task_id]
#         error_message = status['error_message']
#         writer.writerow ( filename , task_id , error_message )
#         logging.error ( 'Ingestion of image %s has failed with message %s' , filename , error_message )


# from multiprocessing import Pool
# import sys
#
# import ee
#
# ee.Initialize ()
#
# import time
# import random
#
#
# def cancel_task(task):
#     print task
#     random_time = random.random ()
#     time.sleep ( 0.5 + random_time * 0.5 )
#     if task.config['state'] in (u'RUNNING' , u'UNSUBMITTED' , u'READY'):
#         print 'canceling %s' % task
#         task.cancel ()
#
#
# def get_tasks():
#     return ee.batch.Task.list ()
#
#
# def usage():
#     print '------------cancel_tasks.py---------------'
#     print '---Cancel all running / pending tasks:'
#     print '     python cancel_tasks.py'
#     print '---Cancel all running / pending tasks containing substring (no regex applied):'
#     print '     python cancel_tasks.py substring'
#
#
# if __name__ == '__main__':
#     if len ( sys.argv ) > 2:
#         usage ()
#         sys.exit ( -2 );
#     tasks = get_tasks ()
#     tasks = [task for task in tasks if task.config['state'] in (u'RUNNING' , u'UNSUBMITTED' , u'READY')]
#
#     if len ( sys.argv ) > 1:
#         tasks = [task for task in tasks if len ( task.config['description'].split ( sys.argv[1] ) ) > 1]
#     print 'cancelling %d tasks' % len ( tasks )
#     p = Pool ( 4 )
#     p.map ( cancel_task , tasks )
#     for task in tasks:
#         cancel_task ( task )

# while(1):
#     try:
#         result = ee.data.getTaskStatus(task.id)[0]
#     except:
#         return "Exception - task not found"
#     state = result['state']
#     if state in ['READY', 'RUNNING']:#
#         print 'Exporting %s ...' %(state)#
#     elif state in ['COMPLETED']:
#         #All GOOD
#         print 'Done %s ...' %(state)
#         return
#     else:
#         print 'Error  %s ...' %(state)

import pandas as pd
from retrying import retry

# specified by user:
# outPutPath = "tasks.csv"
# maxTasks = 10 #Set maximum number of tasks to include in csv file.
#
# taskList = ee.batch.Task.list()
# df = pd.DataFrame()
#
# @retry(wait_exponential_multiplier=10000, wait_exponential_max=100000)
# def checkStatus(task):
#     return ee.batch.Task.status(task)
#
# for i in range(0,min(len(taskList),maxTasks)):
#     dictNew = checkStatus(taskList[i])
#     dfNew = pd.DataFrame(dictNew, index=[i])
#     try:
#         dfNew["calctime(min)"] = (dfNew["update_timestamp_ms"]-dfNew["start_timestamp_ms"])/(1000*60)
#         dfNew["queuetime(min)"] = (dfNew["start_timestamp_ms"]-dfNew["creation_timestamp_ms"])/(1000*60)
#         dfNew["runtime(min)"]= dfNew["queuetime(min)"]+dfNew["calctime(min)"]
#     except:
#         pass
#     df = df.append(dfNew)
#     print i
#
# df.to_csv(path_or_buf=outPutPath)
# print "done"