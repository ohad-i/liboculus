import numpy as np
import cv2
import struct
import argparse
import time
from select import select

## python script shpuld run the oc_client app on the background and kill it on exit, so it should be a close package to hanle all sonar issues

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

'''
struct pipeDataPack{
    unsigned short    syncWord = 0xadad;
    unsigned short    nBeams;
    unsigned short    nRanges;
    float             range;
    float             gain;
    bool              is16Bit;
    int               dataSize;
    unsigned short    dataOffset;
    //unsigned char*   sonarData;
};
'''

def readHeadrMsg(fid):
    syncWord = 0xad
    msgCnt = 0
    
    ret = {}
    while True:
        socks = select([fid], [], [], 0.001)[0]
        if len(socks)>0:
            data = fid.read(21)
            data = struct.unpack('<HHHff?iH', data)
            ret['syncWord'] = data[0]
            ret['nBeams'] = data[1]
            ret['nRanges'] = data[2]
            ret['range'] = data[3]
            ret['gain'] = data[4]
            ret['is16Bit'] = data[5]
            ret['dataSize'] = data[6]
            ret['offset'] = data[7]
            #print(time.time(), '-->', ret)
            return ret

print(pipeFile)

cnt = 0.0
tic = time.time()

with open(pipeFile, 'rb') as fid:
    while True:
        time.sleep(0.001)
        ret = readHeadrMsg(fid)
        dataOffset = ret['offset']*ret['nRanges']
        
        socks = select([fid], [], [], 0.001)
        if len(socks)>0:
            cnt += 1
            sonarData = fid.read(ret['dataSize'])
            
            img = np.frombuffer(sonarData, dtype='uint8').reshape(ret['nBeams'], ret['nRanges'])
            cv2.imshow('aa', img)
            cv2.waitKey(1)
            #import ipdb; ipdb.set_trace()
        
        if time.time()-tic > 3:
            fps = cnt/(time.time()-tic)
            print('sonar fps: %0.2f'%fps)
            tic = time.time()
            cnt = 0
        