#!/usr/bin/python3.7
import configparser
from dataclasses import dataclass, field
from typing import List
from datetime import datetime
import socket
from enum import Enum
from pathlib import Path
import os
import shutil
import io

from serverconnection import ServerConnection

class Priority(Enum):
     Normal = 1
     Night = 2
     High = 3

@dataclass
class Mode:
    name: str
    sort_index: int = 0
    requires_adj_scans: bool = False
    requires_acc: bool = False
    confirmation_mail: str = None
    tag: str = None
    required_server_type: str = None

class Server:
    name: str
    modes: List[Mode]
    path: str


    def __init__(self, name:str, path:str):
        self.name = name
        self.path = path
        self.connection = ServerConnection(path)
        config = configparser.ConfigParser()

        config_file = io.BytesIO()
        self.connection.get('YarraModes.cfg',config_file)
        config_string = config_file.read().decode('UTF-8')
        
        config.read_string(config_string)#;(Path(mnt_path,'YarraModes.cfg'))

        mode_info = ( (mode_entry[1], config[mode_entry[1]])  for mode_entry in config.items('Modes') )

        self.modes = { name: Mode(
                    tag = info.get('tag'),
                    name = info.get('name'),
                    confirmation_mail = info.get('confirmationmail'),
                    requires_adj_scans = info.getboolean('requiresadjscans'),
                    requires_acc = info.getboolean('requiresacc'),
                    required_server_type = info.get('requiredservertype'),
                    sort_index = info.getint('sortindex')
                ) for name, info in mode_info
            }

@dataclass
class TaskData:
    recon_mode: str
    email_notification: str

    scan_protocol: str

    recon_name: str
 
    required_server_type: str

    acc_number: str
    patient_name: str

    scan_file: str
    scan_file_size: int

    param_value: int = None
    priority: Priority = Priority.Normal
    adjustment_files: List[str] = field(default_factory=list)
    system_name: str = socket.gethostname()
    system_vendor: str = 'Siemens'
    system_version: str = 'Unknown'
    yarra_client: str = 'SAC'
    client_version: str = '0.1'
    task_creation_datetime: datetime = field(default_factory=lambda:datetime.now())

    def to_config(self):
        config = configparser.ConfigParser()
        config.optionxform = str
        config['Task'] = dict(
            ReconName = self.recon_name,
            ReconMode = self.recon_mode,
            ScanProtocol = self.scan_protocol,
            ScanFile = self.scan_file,
            AdjustmentFilesCount = str(len(self.adjustment_files)) if self.adjustment_files else '0',
            ParamValue = self.param_value or '0',
            EMailNotification = self.email_notification,
            PatientName = self.patient_name
        )

        config['Information'] = dict(
                SystemName = self.system_name,
                ScanFileSize = self.scan_file_size,
                TaskDate = self.task_creation_datetime.date().isoformat(),
                TaskTime = self.task_creation_datetime.time().isoformat(),
                SystemVendor = self.system_vendor,#  "Siemens");
                SystemVersion = self.system_version,# "Unknown");
                YarraClient = self.yarra_client,#   "SAC");
                ClientVersion = self.client_version,# SAC_VERSION);
                ACC = str(self.acc_number) if self.acc_number is not None else '',
        )
        
        io_file = io.StringIO()
        config.write(io_file)
        io_file.seek(0)
        return io_file.getvalue()

class Task():
    task_name: str 
    scan_file: Path
    task_data: TaskData
    server: Server

    def __init__(self, server, mode_name, scan_file_path, protocol, acc=None, *, email_notifications:list = None, param_value:int=None):
        self.server = server
        if (mode_name not in server.modes.keys()):
            raise Exception(f'Recon mode "{mode_name}" not available on server {server.name}')

        mode = server.modes[mode_name]
        if mode.requires_adj_scans:
            raise Exception(f'Recon mode "{mode_name}" requires adjustments, which aren\'t supported yet')

        if not acc and mode.mode_name:
            raise Exception(f'Recon mode "{mode_name}" requires accession.')

        self.scan_file = Path(scan_file_path)
        if not os.path.exists(self.scan_file):
            raise Exception(f'{self.scan_file} not found')
        self.task_name = self.scan_file.stem

        self.task_data = TaskData(
            scan_file = self.scan_file.name,
            scan_file_size = os.path.getsize(self.scan_file),
            recon_mode = mode_name,
            email_notification = ','.join(email_notifications) if email_notifications else '',
            scan_protocol = protocol,
            recon_name = mode.name,
            param_value = param_value,
            required_server_type = None,
            acc_number = acc,
            patient_name = 'Joe Bloggs',
        )
        # print(self.task_data)

    def submit(self):
        conn = self.server.connection

        conn.lock_task(self.task_name)
        try:
            with open(self.scan_file,'rb') as scan_f:
                conn.store(f'{self.task_name}.task',io.BytesIO(self.task_data.to_config().encode()))
                conn.store(f'{self.task_name}.dat',scan_f)
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