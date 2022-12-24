import numpy as np
import cv2
import struct
import argparse
import time

usageDescription = 'TBD'


parser = argparse.ArgumentParser(description='bluepring oculus sonar interface, %s'%usageDescription, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-r', '--recPath', default=None, help=' path to record folder')
parser.add_argument('-p', '--inPipe', default=None, help=' path to pipe ')
parser.add_argument('-s', '--showSonar', action='store_true', help='show raw sonar data')
'''
parser.add_argument('-s', '--skipFrame', type=int, default=-1, help='start of parsed frame, by frame counter not file index')
parser.add_argument('-q', '--showVideo', action='store_false', help='quite run, if -q - parse only, no show')
parser.add_argument('-f', '--freeRun', action='store_true', help='Not true realtime run')
parser.add_argument('-H', '--highQuality', action='store_true', help='Parse also high quality')
parser.add_argument('-V', '--saveAvi', action='store_true', help='quite run, if -V - create avi files')
'''

args = parser.parse_args()


pipeFile = args.inPipe
recPath = args.recPath
showFlag = args.showSonar

if showFlag:
    winName = 'sonar'
    cv2.namedWindow(winName, 0)

tic = time.time()
cnt = 0


def syncMsg(fid):
    syncWord = 0xadad
    msgCnt = 0
    data = struct.unpack('h', fid.read(2))[0]
    while data != syncWord:
        data = struct.unpack('h', fid.read(2))[0]
        msgCnt += 1
        #print('in->', data, syncWord)
        #import ipdb; ipdb.set_trace()
    print('synced!, size=%d'%msgCnt )
    return True


def sync2Msg(fid):
    syncWord = 2048
    msgCnt = 0
    data = struct.unpack('I', fid.read(4))[0]
    print('-->', data)
    while data != syncWord:
        data = struct.unpack('I', fid.read(4))[0]
        msgCnt += 4
        #print('in->', data, syncWord)
        #import ipdb; ipdb.set_trace()
    print('synced2!, imgOffset=%d'%msgCnt )
    return True

#with open('sonar_8m.oculus', 'rb') as fid:
msgCnt = 0
with open(pipeFile, 'rb') as fid:
    

    while True:
        ret = syncMsg(fid)
        data = fid.read(196)
        #ret = sync2Msg(fid)
        #fid.read(1)
        data = struct.unpack('iII', data[-12:])
        print('data:', data)
        '''
        #data = struct.unpack('h', fid.read(2))[0]
        #print('devId 17936: %d'%data)
        #data = struct.unpack('h', fid.read(2))[0]
        #print('devId 0: %d'%data)
        
        #data = struct.unpack('h', fid.read(2))[0]
        #print('msgId 0x23: %d'%data)

        ttt = fid.read(2048)
        data = fid.read(w*h)
        cnt +=1 

        data = np.frombuffer(data, dtype='uint8').reshape((w, h))
        
        tmp = data+np.min(data)
        im = data #(tmp/np.max(tmp))*255
        print(np.max(im), np.min(im))
        #import ipdb; ipdb.set_trace()

        cv2.imshow(winName, im.astype('uint8'))
        print(cnt)
        key = cv2.waitKey(10)
        if key&0xff== 'q':
            break
        #import ipdb; ipdb.set_trace()
        '''
