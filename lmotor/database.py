import os
import uuid
import typing
import shutil
import hashlib

import lmotor.atlas as atlas
import lmotor.atlas_utils as atlas_utils

class AtlasManager:
    '''use to manage all atlas'''

    def __init__(self, db: atlas.AtlasDatabase, folder:str):
        '''initialize an atlas manager object'''

        self._db = db
        self._folder = folder

    def get_atlas_list(self, pageSize:int, pageIdx:int) -> typing.List:
        '''get atlas list by page size and page index'''

        # get all atlas
        atlas_list = []
        for atlas in self._db.get_atlas_at_page(pageSize, pageIdx):
            atlas_list.append({
                "title" : atlas.Title,
                "uid" : atlas.Uid,
                "count" : atlas.Count,
                "face_path" : atlas.FacePath,
                "source_link" : atlas.SourceLink,
                "has_link": len(atlas.SourceLink) > 0
            })
        return atlas_list
    
    def get_atlas(self, uid:str) -> typing.Optional[atlas.Atlas]:
        '''get atlas by uid'''

        return self._db.get_atlas(uid)
    
    def is_atlas_exists(self, uid:str) -> bool:
        '''check atlas is exists'''

        return self._db.is_atlas_exists(uid)
    
    def delete_atlas(self, uid:str) -> bool:
        '''delete atlas by uid'''

        if self._db.delete_atlas(uid):
            atlas_path = os.path.join(self._folder, uid)
            if os.path.exists(atlas_path):
                shutil.rmtree(atlas_path)
            return True
        return False
    
    def get_sha256(self, folder_name:str) -> str:
        '''get sha256 of folder'''

        return hashlib.sha256(folder_name.encode('utf-8')).hexdigest()

    def upload_local_atlas(self, source_folder:str) -> typing.Tuple[bool, str]:
        '''upload local atlas'''

        # get atlas infos
        success, infos = atlas_utils.handle_local_atlas_infos(source_folder)
        if not success:
            return False, "cannot get folder information"
        
        # copy folder
        sha256 = self.get_sha256(os.path.basename(source_folder))
        target_folder = os.path.join(self._folder, sha256)
        if os.path.exists(target_folder):
            return False, "duplicate folder name which is not supported"
        success = atlas_utils.copy_folder(source_folder, target_folder)
        if not success:
            return False, "copy folder failed"
        
        # insert atlas
        title, filenames = infos
        success = self._db.insert_atlas(sha256, title, target_folder, filenames)
        if not success:
            return False, "insert atlas failed"
        
        # success
        return True, ""

def create_manager(db_path:str, folder:str) -> AtlasManager:
    '''create a manager object'''

    # create database
    try:
        db = atlas.AtlasDatabase(db_path)
        if not os.path.exists(folder):
            return None
        return AtlasManager(db, folder)
    except Exception:
        return None


if __name__ == '__main__':
    manager = create_manager("./datas/app.db", "./datas/atlas")
    success, msg = manager.upload_local_atlas("D:\Projects\Python\E站爬虫\◆FANBOX◆ 38 [30570055＆thirty8ght] [2]")

    print(success, msg)