import os
import natsort
import typing
import shutil

def _calc_page_count(total:int, pageSize:int) -> int:
    '''calculate page count'''

    if total <= 0:return 0
    if pageSize <= 0:return 0

    if total % pageSize == 0:
        return total // pageSize
    return total // pageSize + 1

def get_page_from_list(lst:typing.List, pageSize:int, pageIdx:int) -> typing.List:
    '''get page from list'''

    if pageSize <= 0:
        return []
    startIdx = pageIdx * pageSize
    if startIdx >= len(lst):
        return []
    
    endIdx = min(startIdx + pageSize, len(lst) - 1)
    return lst[startIdx:endIdx]

def handle_local_atlas_infos(folder:str) -> typing.Tuple[bool, typing.Tuple[str, typing.List[str]] ]:
    '''handle local atlas infos'''

    # safe check
    if not os.path.exists(folder) or not os.path.isdir(folder):
        return False, None
    
    # empty check
    files = os.listdir(folder)
    print(files)
    if len(files) == 0:
        return False, None
    
    # get atlas infos
    atlas_title = os.path.basename(folder)
    atlas_filenames = natsort.natsorted(files)
    print(atlas_filenames)
    return True, (atlas_title, atlas_filenames)


def copy_folder(source_folder:str, target_folder:str) -> bool:
    '''copy files from source folder to target folder
    and return True if success, otherwise False
    '''

    # safe check
    if not os.path.exists(source_folder) or not os.path.isdir(source_folder):
        print (f"source folder {source_folder} not exists")
        return False
    
    # create target folder
    parent_folder = os.path.dirname(target_folder)
    if not os.path.exists(parent_folder):
        return False
    
    # copy folder
    os.mkdir(target_folder)
    for file in os.listdir(source_folder):
        src = os.path.join(source_folder, file)
        if os.path.isfile(src):
            dst = os.path.join(target_folder, file)
            shutil.copyfile(src, dst)
    return True