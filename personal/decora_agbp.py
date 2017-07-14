import time
import csv

with open('metadata.csv', 'r') as csvfile:
    csvfile.next()
    imagesreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in imagesreader:
        val = row[3]
        convertito = time.strftime('%m/%d/%Y', time.gmtime(int(val)/1000.))
        print convertito

class SceltaDati(object):

    def __init__(self):
        pass

    def select_images(self):
        pass