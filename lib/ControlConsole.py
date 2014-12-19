__author__ = 'linh'
import sys
import os
import traceback

from twisted.web import xmlrpc
from twisted.web import server
from twisted.python import log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib import ProcessUtil

IDLE = 0
BUSY = 1

SUCCESS = 0
ERR_ERROR = 1
ERR_BUSY = 2
ERR_TIMEOUT = 3

class ControlConsole(xmlrpc.XMLRPC):
    __version__ = '0.2'
    """
    Console used to control station PC
    """
    def __init__(self, host='localhost', port=1000, info={}):
        self.allowNone = True
        self.useDateTime = True
        self.allowedMethods = True
        self._port = port
        self._host = host
        self._info = info
        self._status = IDLE
        self._async_procs = []

    def xmlrpc_ping(self, **kargs):
        """
        Check the connection
        """
        return True

    def xmlrpc_get_status(self, **kargs):
        '''
        Get current status of station
        '''
        return self._status
    def self.nowexit(self):
        os._exit(1)
    def xmlrpc_self_restart(self, **kargs):
        '''
        Self restart this program.
        '''
        # Detect the OS then create schedule task
        import datetime
        import platform
        s = ''
        try:
            addtime = datetime.timedelta(seconds=10)
            exptime = datetime.datetime.now() + addtime
            tm = exptime.minute
            th = exptime.hour
            ts = exptime.second
            if 'linux' in sys.platform:
                # For linux
                s += "Linux\n"
                pass
            else:
                # For windows
                s += "Windows "
                winver = sys.getwindowsversion()
                cmdstr = "python %s" % (os.path.abspath(__file__))

                cmd = [
                    "schtasks", "/create",
                    "/tn", "ControlSelfUpgrade%d" % tm,
                    "/tr", cmdstr,
                    "/sc", "once",
                    "/st", "%02d:%02d:%02d" % (th, tm, ts),
                    "/ru", 'mqx_test',
                    "/rp", 'Freescale3',
                ]
                if winver.major >= 6:
                    # Win 7 +
                    cmd.append('/it')
                    s += "7 +\n"
                else:
                    s += "XP -\n"

                (ret_code, is_timed_out, out_str, err_str) = ProcessUtil.run_job(cmd, is_shell=True)
                s += "%d\n" % ret_code
                t = threading.Timer(1, self.nowexit)
                threading.Timer(1, self.nowexit).start()
        except:
            s += traceback.format_exc()
            return (False, s,)

        return (True, s,)
    def xmlrpc_get_async_status(self, **kargs):
        '''
        Get status of all aysnc processes
        '''
        if len(self._async_procs) == 0:
            return (True, '')
        res = True
        s = "\nStatus of ASYNC processes:\n"
        s += "Platform: %s\n" % (sys.platform)

        for i in range(len(self._async_procs), 0, -1):
            procinfo = self._async_procs[i - 1]
            p = procinfo['proc']
            if not p:
                continue
            fo = procinfo['fo']
            fe = procinfo['fe']

            p.poll()

            s += " - PID: %d\n" % p.pid
            s += " - CMD: %s\n" % '*'.join(procinfo['cmd'])
            if p.returncode is not None:
                # Finished
                s += " - STATUS: Finished\n"
                s += " - RETURN: %d\n" % p.returncode
                (out_str, err_str) = p.communicate()
                if fo:
                    fo.close()
                else:
                    s += " - OUTPUT: %s\n" % out_str
                if fe:
                    fe.close()
                else:
                    s += " - ERROR: %s\n" % str(err_str)
                del(self._async_procs[i - 1])
            else:
                # Un-finished
                s += " - STATUS: Running\n"
                res = False

        return (res, s)

    def xmlrpc_term_async(self):
        if len(self._async_procs) == 0:
            return (True, '')
        res = True
        s = "Terminate async processes:\n"
        s += "Platform: %s\n" % (sys.platform)
        for i in range(len(self._async_procs), 0, -1):
            procinfo = self._async_procs[i - 1]
            p = procinfo['proc']
            if not p:
                continue
            fo = procinfo['fo']
            fe = procinfo['fe']

            p.poll()

            s += " - PID: %d\n" % p.pid
            if p.returncode is not None:
                # Finished
                s += " - STATUS: Finished\n"
                s += " - RETURN: %d\n" % p.returncode
                (out_str, err_str) = p.communicate()
                if fo:
                    fo.close()
                else:
                    s += " - OUTPUT: %s\n" % out_str
                if fe:
                    fe.close()
                else:
                    s += " - ERROR: %s\n" % str(err_str)
            else:
                # Un-finished
                s += " - STATUS: Running ==> WILL BE KILLED\n"
                p.kill()

            del(self._async_procs[i - 1])

        return (res, s)

    def xmlrpc_run_cmd(self, info={}):
        """
        Run command on station PC

        require info:
        active_dir - the directory that command win run from
        command - the command that station will be run
        timeout - the maximum time in (s) that station will wait before kill the process,
                    if timeout is 0 the process will be started then return immediately
        isshell - indicate the command run in shell or not
        output - where the output is writen (file, or return to server)
        error - where the error is writen (file, or return to server)

        return:
        (return_code, output_string, error_string)
        """
        return_code = 1
        output_string = ''
        error_string = ''
        isshell = False
        output = ''
        error = ''
        active_dir = ''
        command = ''
        timeout = 0
        if self._status != IDLE:
            return (ERR_BUSY, '', None)
        self._status = BUSY

        if 'active_dir' in info.keys():
            active_dir = info['active_dir']
        if 'command' in info.keys():
            command = info['command']
        if 'timeout' in info.keys():
            timeout = info['timeout']
        if 'isshell' in info.keys():
            isshell = info['isshell']
        if 'output' in info.keys():
            output = info['output']
        if 'error' in info.keys():
            error = info['error']

        try:
            if active_dir:
                # Change to active dir if available
                curdir = os.getcwd()
                if os.path.exists(active_dir) and os.path.isdir(active_dir):
                    os.chdir(active_dir)

            cmd = []
            if isinstance(command, list) or isinstance(command, tuple):
                cmd.extend(command)
            else:
                cmd.append(command)
            if timeout == 0:
                (res, proc, fo, fe) = ProcessUtil.run_async_job(cmd, is_shell=isshell, output=output, error=error)
                if res == 0:
                    tmp = {
                        'proc': proc,
                        'fo': fo,
                        'fe': fe,
                        'cmd': cmd,
                    }
                    self._async_procs.append(tmp)
                    return_code = res
                else:
                    raise Exception("Can not run command as async. Detail: \n%s" % str(proc))
            else:
                (return_code, is_timeout, output_string, error_string) = ProcessUtil.run_job(cmd, timeout, is_shell=isshell, output=output, error=error)

            if active_dir:
                # Change back to previous dir
                os.chdir(curdir)
        except:
            error_string = traceback.format_exc()
            return_code = ERR_ERROR
        finally:
            self._status = IDLE

        return (return_code, output_string, error_string,)

def main():
    from twisted.internet import reactor
    log.startLogging(sys.stdout)
    r = ControlConsole('localhost', 1099)
    reactor.listenTCP(1099, server.Site(r))
    reactor.run()

if __name__ == '__main__':
    main()
