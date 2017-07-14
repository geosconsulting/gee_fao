from multiprocessing import Pool
import sys
import time
import random
import ee
ee.Initialize()

_L1_AET_DEKADAL = ee.ImageCollection("users/fabiolananotizie/L1_AET")

def select_rasters(start,end):

    collection_filtered = _L1_AET_DEKADAL.filterDate(
                start,
                end)

    rasters_selected = collection_filtered.getInfo()
    rasters_selected_num = collection_filtered.size().getInfo()

    raster_names_selected= []
    for index in range(0,rasters_selected_num):
        raster_names_selected.append(rasters_selected['features'][index]['id'])

    return raster_names_selected

def get_tasks_list():
    return ee.data.getTaskList()

def get_tasks():
    return ee.batch.Task.list ()

def running_tasks(tasks):
    tasks_running = [task for task in tasks if task.config['state'] in (u'RUNNING' , u'UNSUBMITTED' , u'READY')]

    if len ( tasks_running ) == 0:
        print "No tasks running at the moment"
    else:
        print "Tasks running at the moment " , len ( tasks_running )

    name_asset_in_upload = []
    for running in tasks_running:
        status = running.status ()
        # print status['task_type']
        # print status['description']
        # print status['id']
        # print running.active ()
        name_asset_in_upload.append(status['description'])

    return tasks_running,name_asset_in_upload

def completed_cancelled_tasks(tasks):
    tasks_completed_cancelled = [task for task in tasks if task.config['state'] in (u'COMPLETED',u'CANCELLED')]
    return tasks_completed_cancelled

def failed_tasks(tasks):
    tasks_failed = [task for task in tasks if task.config['state'] in (u'FAILED')]

    for failed in tasks_failed:
        task_id = failed.status()['id']
        image_id = failed.status ()['description']
        error_message = failed.status()['error_message']
        print( 'Ingestion of image %s with id %s has failed with message %s' % (image_id ,task_id , error_message ))

def cancel_task(task):
    print task
    random_time = random.random ()
    time.sleep ( 0.5 + random_time * 0.5 )
    if task.config['state'] in (u'RUNNING' , u'UNSUBMITTED' , u'READY'):
        print 'cancelling %s' % task
        task.cancel ()

if __name__ == '__main__':

    gee_root = 'projects/fao-wapor/'
    fab_root = 'users/fabiolananotizie/'

    tasks_list = get_tasks_list()

    tasks = get_tasks ()
    rst_uploading = running_tasks(tasks)
    print rst_uploading[1]
    temporary_rst_uploading = rst_uploading[0]

    st = '2015-1-1'
    en = '2015-1-31'
    rsts_selected = select_rasters(st,en)
    print rsts_selected

    if rst_uploading in rsts_selected:
        print "In the list of requested files"
    else:
        print "Not in the list of requested files"

    # p = Pool ( 4 )
    # p.map ( cancel_task , tasks )
