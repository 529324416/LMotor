import os
import json
import difflib
import sqlalchemy

from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy import Column, String, Integer, Text
from typing import List

import lmotor.atlas_utils as atlas_utils

class Base(DeclarativeBase):
    pass

class Atlas(Base):
    '''define a class to store atlas information'''

    __tablename__ = "atlas"

    Id = Column(Integer, primary_key=True)
    Uid = Column(String)
    Title = Column(String)
    FolderPath = Column(String)
    Filenames = Column(Text)
    Count = Column(Integer)
    FacePath = Column(String)
    SourceLink = Column(String)

    def __repr__(self) -> str:
        return f"Atlas({self.Title}, {self.Uid}, {self.Count}, {self.FolderPath}, {self.Filenames}, {self.FacePath}, {self.SourceLink})"
    
    # def get_images(self, pageSize:int, pageIdx:int) -> List[str]:
    #     '''get images by page size and page count'''

    #     if self.imgs is None:
    #         self.imgs = self.Filenames.split("/")
    #     return atlas_utils.get_page_from_list(self.imgs, pageSize, pageIdx)


class AtlasDatabase:
    '''define a class to store atlas database'''

    def __init__(self, db_path, echo=False):
        '''initialize an atlas database object'''

        self.db_path = db_path
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_path}", echo=echo)
        Base.metadata.create_all(self.engine)

    def insert_atlas(self, uid, title, folder_path, filenames, source_link = "") -> bool:
        '''insert an atlas into atlas database
        the total data must be valid before insert
        return True if success, otherwise False
        '''

        try:
            with Session(self.engine) as session:
                atlas = Atlas(
                    Uid=uid,
                    Title=title, 
                    FolderPath=folder_path, 
                    Filenames = json.dumps(filenames),
                    Count=len(filenames), 
                    FacePath=os.path.join(folder_path, filenames[0]),
                    SourceLink=source_link,
                )
                session.add(atlas)
                session.commit()
                return True
        except Exception:
            return False
        
    def delete_atlas(self, unique_id:int) -> bool:
        '''delete an atlas from atlas database
        return True if success, otherwise False
        '''

        try:
            with Session(self.engine) as session:
                _selection = sqlalchemy.delete(Atlas).where(Atlas.Uid == unique_id)
                session.execute(_selection)
                session.commit()
                return True
        except Exception:
            return False
        
    def get_atlas_at_page(self, page_size:int, page_idx:int) -> List[Atlas]:
        '''query atlas with page mode, return atlas list
        for example, given page size = 10 and page idx = 1, return atlas list [10, 20]
        '''

        with Session(self.engine) as session:
            _selection = sqlalchemy.select(Atlas).limit(page_size).offset(page_size * page_idx)
            return session.scalars(_selection).all()
    
    def query_atlas_by_title(self, table_name:str, title:str, ratio_threshold:float) -> List[Atlas]:
        '''query atlas by title, return atlas list'''

        sql = f"SELECT * FROM {table_name}"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if result is None:
            return None
        
        buffer = []
        for item in result:
            _similarity = difflib.SequenceMatcher(None, title, item[1]).ratio()
            if _similarity >= ratio_threshold:
                buffer.append(Atlas(*item))
        return buffer

    def get_atlas(self, unique_id:int) -> Atlas:
        '''get atlas by table name and unique id'''

        with Session(self.engine) as session:
            _selection = sqlalchemy.select(Atlas).where(Atlas.Uid == unique_id)
            _result = session.scalars(_selection).first()
            return _result
        
    def is_atlas_exists(self, unique_id:int) -> bool:
        '''check atlas is exists'''

        with Session(self.engine) as session:
            _selection = sqlalchemy.select(Atlas).where(Atlas.Uid == unique_id)
            _result = session.scalars(_selection).first()
            return _result is not None


if __name__ == "__main__":
    '''test database'''

    db = AtlasDatabase("./datas/database.db")
    _id = db.insert_atlas("test", "./datas/atlas/test", ["test1.png", "test2.jpg", "test3.png"])
    print(_id)

    result = db.get_atlas_at_page(10, 0)
    print(result)