#!/usr/bin/python3.7
import configparser
#from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import socket
from enum import Enum
from pathlib import Path
import os
import shutil
import io
from .serverconnection import ServerConnection

class Priority(Enum):
     Normal = 1
     Night  = 2
     High   = 3


class Mode():
    name = None  # type: str
    sort_index = 0  # type: int
    requires_adj_scans = None # type: bool = False
    requires_acc = None  # type: bool = False
    confirmation_mail = None  # type: str = None
    tag = None  # type: str = None
    required_server_type = None  # type: str = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return self.name +","+ str(self.sort_index)

class Server():
    name = None # type: str
    modes = None # type: List[Mode]
    path = None # type: str

    def connection(self):
        return ServerConnection(self.path)

    def __init__(self, name,path):
        #super(Server, self).__init__()
        self.name = name
        self.path = path
        
        config = configparser.ConfigParser()
        config_file = io.BytesIO()

        with self.connection() as c:
            c.get('YarraModes.cfg',config_file)

        config_string = config_file.read().decode('UTF-8')
        config.read_string(config_string)#;(Path(mnt_path,'YarraModes.cfg'))

        mode_info = ( (mode_entry[1], config[mode_entry[1]])  for mode_entry in config.items('Modes') )

        self.modes = {
             name: Mode(
                tag =                info.get('tag'),
                name =               info.get('name'),
                confirmation_mail =  info.get('confirmationmail'),
                requires_adj_scans = info.getboolean('requiresadjscans'),
                requires_acc =       info.getboolean('requiresacc'),
                required_server_type = info.get('requiredservertype'),
                sort_index =         info.getint('sortindex')
            ) for name, info in mode_info
        }

class TaskData():
    recon_mode = None # type: str
    email_notification = None # type: str

    scan_protocol = None # type: str

    recon_name = None # type: str
 
    required_server_type  = None # type: str

    acc_number = None # type: str
    patient_name = None # type: str

    scan_file = None # type: str
    scan_file_size = None # type: int

    param_value = None # type: int
    priority  = Priority.Normal # type: Priority
    adjustment_files =   None # type: List[str] 
    system_name =        socket.gethostname() # type: str 
    system_vendor =      'Siemens' # type: str 
    system_version =     'Unknown' # type: str 
    yarra_client =       'SAC' # type: str 
    client_version =     '0.1' # type: str 
    task_creation_datetime = None # type: datetime 

    def __init__(self, **kwargs):
        self.task_creation_datetime = datetime.now()
        self.adjustment_files = []
        self.__dict__.update(kwargs)

    def to_config(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config['Task'] = dict(
            ReconName =     self.recon_name,
            ReconMode =     self.recon_mode,
            ScanProtocol =  self.scan_protocol,
            ScanFile =      self.scan_file,
            AdjustmentFilesCount = str(len(self.adjustment_files)) if self.adjustment_files else '0',
            ParamValue =    self.param_value or '0',
            EMailNotification = self.email_notification,
            PatientName =   self.patient_name
        )

        config['Information'] = dict(
                SystemName =    self.system_name,
                ScanFileSize =  self.scan_file_size,
                TaskDate =      self.task_creation_datetime.date().isoformat(),
                TaskTime =      self.task_creation_datetime.time().isoformat(),
                SystemVendor =  self.system_vendor,
                SystemVersion = self.system_version,
                YarraClient =   self.yarra_client,
                ClientVersion = self.client_version,
                ACC =           str(self.acc_number) if self.acc_number is not None else '',
        )
        
        io_file = io.StringIO()
        config.write(io_file)
        io_file.seek(0)
        return io_file.getvalue()

class Task():
    task_name = None # type: str 
    scan_file = None # type: Path
    task_data = None # type: TaskData
    server = None # type: Server

    def __init__(self, server, mode_name, scan_file_path, protocol, patient_name, acc=None, *, email_notifications:list = None, param_value:int=None):
        self.server = server
        if (mode_name not in server.modes.keys()):
            raise Exception('Recon mode "{mode_name}" not available on server {server.name}'.format(**locals()))

        mode = server.modes[mode_name]
        if mode.requires_adj_scans:
            raise Exception('Recon mode "{mode_name}" requires adjustments, which aren\'t supported yet'.format(**locals()))

        if not acc and mode.mode_name:
            raise Exception('Recon mode "{mode_name}" requires accession.'.format(**locals()))

        self.scan_file = Path(scan_file_path)
        if not os.path.exists(self.scan_file):
            raise Exception('{self.scan_file} not found'.format(**locals()))
        self.task_name = self.scan_file.stem

        self.task_data = TaskData(
            scan_file =      self.scan_file.name,
            scan_file_size = os.path.getsize(self.scan_file),
            recon_mode =     mode_name,
            email_notification = ','.join(email_notifications) if email_notifications else '',
            scan_protocol =  protocol,
            recon_name =     mode.name,
            param_value =    param_value,
            required_server_type = None,
            acc_number =     acc,
            patient_name =   patient_name,
        )
        # print(self.task_data)

    def submit(self):
        with self.server.connection() as conn:
            conn.lock_task(self.task_name)
            try:
                with open(self.scan_file,'rb') as scan_f:
                    conn.store('{self.task_name}.task'.format(**locals()), io.BytesIO(self.task_data.to_config().encode()))
                    conn.store('{self.task_name}.dat'.format(**locals()), scan_f)
            finally:
                conn.unlock_task(self.task_name)

        # with SoftFileLock(Path(self.server.path,self.task_name+'.lock'), timeout=1):
        #     task_loc = Path(self.server.path,self.task_name+'.task')
        #     with open(task_loc,'w') as f:
        #         self.task_data.to_config().write(f)
        #     try:
        #         shutil.copy(self.scan_file, Path(self.server.path,self.task_name+'.dat'))
        #     except Exception as e:
        #         os.remove(task_loc)
        #         raise e