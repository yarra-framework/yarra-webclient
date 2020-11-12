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
from smb.smb_structs import OperationFailure
import hashlib

class Priority(Enum):
    Normal = 1
    Night  = 2
    High   = 3

    def __str__(self):
        return self.name

# class Mode():
#     name = None  # type: str
#     sort_index = 0  # type: int
#     requires_adj_scans = None # type: bool = False
#     requires_acc = None  # type: bool = False
#     confirmation_mail = None  # type: str = None
#     tag = None  # type: str = None
#     required_server_type = None  # type: str = None

#     def __init__(self, **kwargs):
#         self.__dict__.update(kwargs)

#     def __repr__(self):
#         return self.name +","+ str(self.sort_index)

# class Server():
#     name = None # type: str
#     modes = None # type: List[Mode]
#     path = None # type: str

#     def connection(self):
#         return ServerConnection(self.path)

#     def __init__(self, name,path, lazy=False):
#         #super(Server, self).__init__()
#         self.name = name
#         self.path = path
        
#         config = configparser.ConfigParser()
#         config_file = io.BytesIO()

#         if not lazy:
#             with self.connection() as c:
#                 c.get('YarraModes.cfg',config_file)

#             config_string = config_file.read().decode('UTF-8')
#             config.read_string(config_string)#;(Path(mnt_path,'YarraModes.cfg'))

#             mode_info = ( (mode_entry[1], config[mode_entry[1]])  for mode_entry in config.items('Modes') )

#             self.modes = {
#                  name: Mode(
#                     tag =                info.get('tag'),
#                     name =               info.get('name'),
#                     confirmation_mail =  info.get('confirmationmail'),
#                     requires_adj_scans = info.getboolean('requiresadjscans'),
#                     requires_acc =       info.getboolean('requiresacc'),
#                     required_server_type = info.get('requiredservertype'),
#                     sort_index =         info.getint('sortindex')
#                 ) for name, info in mode_info
#             }

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
    task_name = None

    scan_file_hash = None
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
            ScanFileHash =  self.scan_file_hash,
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
        if self.adjustment_files:
            config['AdjustmentFiles'] = {}
            for i,f in enumerate(self.adjustment_files):
                config['AdjustmentFiles'][ '%{:02x}'.format(i).upper()] = "{}_{}.dat".format(self.task_name,i)
                config['AdjustmentFiles']['OriginalName_{}'.format(i)] = f
        
        io_file = io.StringIO()
        config.write(io_file)
        io_file.seek(0)
        return io_file.getvalue()

    def __repr__(self):
        return self.__dict__.__repr__()

class Task():
    task_name = None # type: str 
    scan_file = None # type: Path
    task_data = None # type: TaskData
    server = None # type: Server

    @staticmethod
    def from_other(t):
        return Task(t.mode, t.scan_file_path, t.protocol, t.patient_name, t.name, t.accession, t.priority, t.extra_files)

    def __init__(self, mode, scan_file_path, protocol, patient_name, task_name, acc=None, priority = Priority.Normal, extra_files=None, *, email_notifications = None, param_value=None):
        self.mode = mode
        self.task_name = task_name
        self.extra_files = extra_files

        if not acc and mode.requires_acc:
            raise Exception('Recon mode "{}" requires accession.'.format(mode.name))

        self.scan_file = Path(scan_file_path)
        if not os.path.exists(scan_file_path):
            raise Exception('{} not found'.format(self.scan_file))
        self.task_data = TaskData(
            task_name = task_name,
            scan_file =      self.task_name+".dat",
            scan_file_size = os.path.getsize(scan_file_path),
            recon_mode =     mode.name,
            email_notification = ','.join(email_notifications) if email_notifications else '',
            scan_protocol =  protocol,
            recon_name =     mode.desc,
            param_value =    param_value,
            required_server_type = None,
            acc_number =     acc,
            patient_name =   patient_name,
            priority = priority,
            adjustment_files = extra_files
        )
        # print(self.task_data)

    def __repr__(self):
        return self.task_data.__repr__()

    def submit(self):
        with self.mode.server.connection() as conn:
            try:
                conn.lock_task(self.task_name)
            except:
                raise Exception("task appears to be locked")

            task_file = '{}.task'.format(self.task_name)
            if self.task_data.priority == Priority.Night:
                task_file += '_night'
            elif self.task_data.priority == Priority.High:
                task_file += '_prio'

            try:
                with open(str(self.scan_file),'rb') as scan_f:
                    task_data.scan_file_hash = hashlib.md5(scan_f.read()).hexdigest()
                    conn.store(self.task_name, self.task_data.scan_file, scan_f)
                if self.extra_files:
                    for i, file in enumerate(self.extra_files):
                        with open(str(file),'rb') as f:
                            conn.store(self.task_name, "{}_{}.dat".format(self.task_name,str(i)), f)
                conn.store(self.task_name, task_file, io.BytesIO(self.task_data.to_config().encode()))

            except Exception as e:
                # Clean up...
                try:
                    conn.delete(self.task_name, self.task_data.scan_file)
                except OperationFailure: pass
                try:
                    conn.delete(self.task_name, task_file)
                except OperationFailure: pass

                if self.extra_files:
                    for i in range(len(self.extra_files)):
                        try:
                            conn.delete(self.task_name,  "{}_{}.dat".format(self.task_name,str(i)))
                        except OperationFailure: pass

                raise e
            finally:
                conn.unlock_task(self.task_name)