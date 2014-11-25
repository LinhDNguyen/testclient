'''
Created on Mar 1, 2013

@author: mqx_test
'''
import threading
import serial
import time
import re
import datetime


class COMAccess(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, thname, com_number, baudrate):
        '''
        Constructor
        '''
        threading.Thread.__init__(self)
        self.name = thname
        self.comNumber = com_number
        self.baudrate = baudrate

        self.isFinish = False
        self.readString = ""
        self.writeString = ""
        self.currentString = ""
        self.currentWithTime = ""
        self.comConnection = None
        self._isError = False
        self.errorStr = ""
        self.termChar = "\r\n"

    def getTermChar(self):
        return self.termChar

    def setTermChar(self, termCh="\r\n"):
        self.termChar = termCh
        return self.termChar

    def finish(self, willFinish):
        self.isFinish = willFinish
        return self.isFinish

    def isFinish(self):
        return self.isFinish

    def isError(self):
        return self._isError

    def getErrorStr(self):
        return self.errorStr

    def getAll(self):
        return self.readString

    def getCurrent(self):
        return self.currentString

    def getCurrentWithTime(self):
        return self.currentWithTime

    def clearCurrent(self):
        self.currentString = ""
        self.currentWithTime = ""
        return self.currentString

    def clearCurrentOnly(self):
        self.currentString = ""

    def clearAll(self):
        self.readString = ""
        self.writeString = ""
        return self.readString + self.writeString

    def write(self, writeStr):
        self.writeString += writeStr

    def writeLine(self, writeStr):
        self.writeString += writeStr + self.termChar

    def getTimeStamp(self):
        now = datetime.datetime.now()
        return now.strftime("%H:%M:%S.%f ")

    def waitFor(self, waitStr, timeOut=0):
        print "\t+++++Wait for [", waitStr, "] in", timeOut, "+++++"
        found = False
        i = 0
        tsleep = 0.05

        while(True):
            curStr = self.currentString
            if isinstance(waitStr, list) or isinstance(waitStr, tuple):
                for wStr in waitStr:
                    res = re.search(wStr, curStr, re.I | re.M)
                    if res is not None:
                        found = True
                        print "\t-----String   [", wStr, "] found.-----"
                if found:
                    break
            else:
                res = re.search(waitStr, self.currentString, re.I | re.M)
                if res is not None:
                    print "\t-----String   [", waitStr, "] found.-----"
                    found = True
                    break

            time.sleep(tsleep)
            if (timeOut > 0) and (i >= (timeOut / tsleep)):
                break

            i += 1

        return found

    def run(self):
        print "Starting COM ", self.comNumber, " thread."
        ser = None
        # Init COM port as non-blocking read/write
        try:
            ser = serial.Serial(port=self.comNumber, baudrate=self.baudrate, timeout=0)

            # Start the loop
            while(False == self.isFinish):
                # Read input buffer
                ch = ser.read(1000)
                if((len(ch) > 0) and ("\n" != ch)):
                    self.readString += ch
                    self.currentString += ch
                    self.currentWithTime += ch.replace('\n', '\n' + self.getTimeStamp())
                writen_bytes = 0

                # If have something need to write, write it
                if(len(self.writeString) > 0):
                    writen_bytes = ser.write(self.writeString)
                    if(writen_bytes > 0):
                        # Remove writen string from writeString
                        self.writeString = self.writeString[writen_bytes:]
                # Flush serial
                ser.flush()
                # Sleep to reduce CPU effort
                time.sleep(0.01)
            print "Finish the COM!!!"
        except Exception as ex:
            self.errorStr += str(ex)
            if(ser):
                ser.close()
            self._isError = True
        finally:
            if(ser):
                ser.close()

if __name__ == '__main__':
    com3 = COMAccess('COM3 thread', 8, 115200)
    com4 = COMAccess('COM4 thread', 10, 115200)

    # Start
    com3.start()
    com4.start()

    # read and write operation
    com3.write("This is first text from COM3\n")
    time.sleep(0.1)
    com3.write("This is second text from COM3\n")
    time.sleep(0.1)

    com4.write("This is first text from COM4\n")
    time.sleep(0.1)

    com3.write("This is third text from COM3\n")
    time.sleep(0.1)
    print "Current text of COM3:"
    print com3.getAll()
    print "COM3 clear all:", com3.clearAll()
    com4.write("This is second text from COM4\n")
    time.sleep(1)

    print "Text of COM3: ", com3.getAll()
    print "Text of COM4: ", com4.getAll()

    # finish
    print "Finish all!!!"
    com3.finish(True)
    com4.finish(True)

    # Thread safe, join to wait it really finish
    com3.join()
    com4.join()
