import socket
import io
from pathlib import Path
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

class ServerConnection:
    server_name = None
    dead = False 
    username = None
    password = None
    def __init__(self, server_name, username, password):
        self.server_name = server_name
        self.username = username
        self.password = password

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self,type,value,traceback):
        self.close();

    def connect(self):        
        if (self.dead):
            raise Exception("dead connection raised to life")
        print("Connecting to",self.server_name)
        self.conn = SMBConnection(self.username, self.password, 'yarra-client', self.server_name)
        self.conn.connect(self.server_name)

    def close(self):
        self.dead = True
        print("Disconnected from",self.server_name)
        self.conn.close()

    def file_exists(self,name):
        try: 
            self.conn.getAttributes('YarraServer',name)
            return True
        except OperationFailure as e:
            return False

    def task_locked(self,task_name):
        return self.file_exists('{}.lock'.format(task_name))

    def lock_task(self, task_name):
        if (self.task_locked('{}.lock'.format(task_name))):
            raise Exception("task already locked")
        self.conn.storeFile('YarraServer','{}.lock'.format(task_name),io.BytesIO(b"lock"))        

    def unlock_task(self, task_name):
        if self.task_locked(task_name):
            self.conn.deleteFiles('YarraServer','{}.lock'.format(task_name))        
        else:
            raise Exception('{} does not appear to be locked'.format(task_name))

    def delete(self, task_name, file):
        if self.task_locked(task_name):
            self.conn.deleteFiles('YarraServer',file)       
        else:
            raise Exception('{} does not appear to be locked'.format(task_name))


    def store(self, task_name, file_name, file_obj, *, force=False):
        print("Storing file {}".format(file_name))
        path = Path(file_name)

        if self.task_locked(task_name):
            if not force and self.file_exists(path.name):
                raise Exception('{} exists on server'.format(path.name))
            self.conn.storeFile('YarraServer',path.name,file_obj)
        else:
            raise Exception('{} does not appear to be locked'.format(task_name))
            
        print("Stored file")

    def get(self, file_name, file_obj):
        self.conn.retrieveFile('YarraServer',file_name,file_obj)
        file_obj.seek(0)

if __name__ == "__main__":
    test = ServerConnection('***REMOVED***')
    test.lock_task('test2')

    try:
        with io.BytesIO(b'test') as f:
            test.store('test2.dat',f)
    finally:
        test.unlock_task('test2')

    sharedfiles = test.conn.listPath('YarraServer', '/')

    for sharedfile in sharedfiles:
        print(sharedfile.filename)