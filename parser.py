import numpy as np
import cv2
import struct

h = 256
w = 704
winName = 'input'
#cv2.namedWindow(winName, 0)
cnt = 0


def syncMsg(fid):
    syncWord = 0x4f53
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
with open('out.bin', 'rb') as fid:
    #import ipdb; ipdb.set_trace()
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
