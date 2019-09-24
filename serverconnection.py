import fs.smbfs
import socket
import io
from pathlib import Path
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

class ServerConnection:
    def __init__(self, server_name):
        user = 'yarra'
        password = '***REMOVED***'
        self.conn = SMBConnection(user, password, 'yarra-client', server_name)
        self.conn.connect(server_name)

    def file_exists(self,name):
        try: 
            self.conn.getAttributes('YarraServer',name)
            return True
        except OperationFailure as e:
            return False


    def task_locked(self,task_name):
        return self.file_exists(f'{task_name}.lock')

    def lock_task(self, task_name):
        self.conn.storeFile('YarraServer',f'{task_name}.lock',io.BytesIO(b"lock"))        

    def unlock_task(self, task_name):
        if self.task_locked(task_name):
            self.conn.deleteFiles('YarraServer',f'{task_name}.lock')        
        else:
            raise Exception(f'{task_name} does not appear to be locked')

    def store(self, file_name, file_obj, *, force=False):
        path = Path(file_name)
        if not force and self.file_exists(path.name):
            raise Exception(f'{path.name} exists on server')

        self.conn.storeFile('YarraServer',path.name,file_obj)
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