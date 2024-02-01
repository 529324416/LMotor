from lmotor.database import create_manager

class FastMotor:
    '''bind lmotor and fastapi together'''

    def __init__(self, db_path = "./datas/app.db", atlas_folder_path = "./datas/atlas"):
        '''initialize an lmotor object'''

        print(f"create database from {db_path}")
        self.atlas_manager = create_manager(db_path, atlas_folder_path)
        if self.atlas_manager is None:
            raise Exception("create atlas manager failed")