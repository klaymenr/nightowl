import paramiko
import urllib
import cStringIO
from PIL import Image


class Camera ():
    def __init__(self, creds):
        self.__ip = creds['ip']
        self.__username = creds['username']
        self.__password = creds['password']

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.__ip, username=self.__username, password=self.__password)
        self.__ssh = ssh

    def manual_daynight(self):
        manual_irled = "/bin/ubnt_ipc_cli -T='ubnt_ispserver' -m='{\"functionName\":\"ChangeIspSettings\",\"irLedMode\":\"manual\" \"irLedLevel\": 215}'"
        self.ssh_command(manual_irled)

    def auto_daynight(self):
        auto_irled = "/bin/ubnt_ipc_cli -T='ubnt_ispserver' -m='{\"functionName\":\"ChangeIspSettings\",\"irLedMode\":\"auto\"}'"
        self.ssh_command(auto_irled)

    def ssh_command(self, command):
        ssh = self.__ssh
        stdin_ssh, stdout_ssh, stderr_ssh = ssh.exec_command(command)
        exit_status = stdout_ssh.channel.recv_exit_status()
        if exit_status != 0:
            print('exit_status {}, command {}'.format(exit_status, command))

    def systemcfg_write(self, stuff):
        for name, value in stuff.iteritems():
            command = "/usr/bin/ubnt_system_cfg write {} {}".format(name, value)
            self.ssh_command(command)

    def anon_snapshot(self, enable):
        stuff = {}
        stuff['httpd.anonSnapshot'] = 1 if enable is True else 0
        self.systemcfg_write(stuff)

    def snapshot(self):
        ip = self.__ip
        url = "http://" + ip + "/snap.jpeg"
        snapshot = cStringIO.StringIO(urllib.urlopen(url).read())
        return Image.open(snapshot)

    def daynight(self, mode):
        if mode == 'day':
            command = 'echo 1 > /proc/gpio/icr_fbc; echo 0 > /proc/gpio/icr_enb ; sleep 2; echo 1 > /proc/gpio/icr_enb'
        elif mode == 'night':
            command = 'echo 0 > /proc/gpio/icr_fbc; echo 0 > /proc/gpio/icr_enb ; sleep 2; echo 1 > /proc/gpio/icr_enb'
        self.ssh_command(command)

    def pmask(self, settings):
        ipc_cli = "/usr/bin/ubnt_ipc_cli -T=ubnt_ispserver -r=1 "
        command = "{} -m='{\"functionName\": \"ChangeIspSettings\", {} }'".format(ipc_cli, settings)
        print "{}".format(command)
#         self.ssh_command(settings)

