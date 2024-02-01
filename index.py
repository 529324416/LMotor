import os
import json
import shutil
import hashlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder

from fast_motor import FastMotor
from ants.spider_manager import run_ehspider

# initialize path
folder_root = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/").lower()
folder_static = f"{folder_root}/src/static".lower()
folder_templates = f"{folder_root}/src/templates".lower()
folder_gallery = f"{folder_static}/gallery".lower()
folder_database = f"{folder_root}/datas".lower()

if not os.path.exists(folder_database):
    os.mkdir(folder_database)

# initialize system
app = FastAPI(title="LMotor", description="Provide Image Downloaded and Viewer Function", version="1.0.0")
templates = Jinja2Templates(directory=folder_templates)
staticFiles = StaticFiles(directory=folder_static, html=True)

motor = FastMotor(f"{folder_database}/app.db", folder_gallery)
app.mount("/static", staticFiles, name="static")

print(f"static folder path: {folder_static}")

def url_for_static(filepath:str) -> str:
    '''return url for static file'''

    return filepath.lower().replace("\\","/").replace(folder_static,"")

def get_sha256(string: str) -> str:

    return hashlib.sha256(string.encode()).hexdigest()

def clear_invalid_folders():
    '''read all local gallery folders and if these folders 
    not exists in database, then delete these folders'''

    print("clear invalid folders")
    folder_list = os.listdir(folder_gallery)
    for folder in folder_list:
        if not motor.atlas_manager.is_atlas_exists(folder):
            folder_path = os.path.join(folder_gallery, folder)
            if os.path.isdir(folder_path):
                print(f"delete folder: {folder_path}")
                # os.rmdir(folder_path)
                shutil.rmtree(folder_path)

clear_invalid_folders()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    '''return home page'''

    ctx = {
        "request" : request
    }
    return templates.TemplateResponse(name = "index.html", context = ctx)

@app.get("/card-example", response_class=HTMLResponse)
async def card_example(request: Request):
    '''return card example page'''

    ctx = {
        "request" : request
    }
    return templates.TemplateResponse(name = "example/card_content.html", context = ctx)


# about content page
@app.get("/ui/content/gallery", response_class=HTMLResponse)
async def ui_content_gallery(request:Request) -> HTMLResponse:
    '''return gallery page'''

    return await ui_content_gallery_page(0, request)

@app.get("/ui/content/gallery/{page}", response_class=HTMLResponse)
async def ui_content_gallery_page(page, request: Request):
    '''return gallery page'''

    atlas_list = motor.atlas_manager.get_atlas_list(32, page)
    for item in atlas_list:
        item["face_path"] = url_for_static(item["face_path"])

    if len(atlas_list) == 0:
        return templates.TemplateResponse(name = "content/error.html", context = { "request" : request, "title" : "No Atlas Now"})

    ctx = { 
        "request" : request,
        "atlas_list" : atlas_list
    }
    return templates.TemplateResponse(name = "content/gallery.html", context = ctx)

@app.get("/ui/content/atlas/{uid}", response_class=HTMLResponse)
async def ui_content_atlas_uid(uid, request: Request):
    '''return atlas page'''

    atlas = motor.atlas_manager.get_atlas(uid)
    if atlas is None:
        return templates.TemplateResponse(name = "content/error.html", context = { "request" : request, "title" : "404 Not Found"})

    ctx = { 
        "request" : request,
        "atlas" : {
            "title" : atlas.Title,
            "uid" : atlas.Uid,
            "count" : atlas.Count,
            "face_path" : url_for_static(atlas.FacePath),
            "source_link" : atlas.SourceLink,
            "has_link": len(atlas.SourceLink) > 0,
            "images": [
                url_for_static(os.path.join(atlas.FolderPath, filename)) for filename in json.loads(atlas.Filenames)
            ]
        }
    }
    return templates.TemplateResponse(name = "content/view_atlas.html", context = ctx)

# about functions
@app.get("/ui/function/upload", response_class=HTMLResponse)
async def ui_function_upload(request: Request):
    '''return upload page'''

    ctx = {"request" : request}
    return templates.TemplateResponse(name = "function/upload.html", context = ctx)


# about api

@app.post("/api/atlas/delete", response_class=JSONResponse)
async def api_atlas_delete(request: Request) -> JSONResponse:
    '''delete atlas by uid'''

    jsonData = await request.json()
    uid = jsonData["uid"]
    success = motor.atlas_manager.delete_atlas(uid)
    result = jsonable_encoder({ "ret" : success })
    return JSONResponse(content=result, headers={"Content-Type": "application/json"})

@app.post("/api/upload/local_folder", response_class=JSONResponse)
async def api_upload_local_folder(request: Request):
    '''upload local folder'''

    # get folder path
    jsonData = await request.json()
    folder_path = jsonData["folder_path"]
    success, message = motor.atlas_manager.upload_local_atlas(folder_path)
    result = jsonable_encoder({"ret":success, "msg": message})
    return JSONResponse(content=result, headers={"Content-Type": "application/json"})

# @app.post("/api/spider/ehentai", response_class=JSONResponse)
@app.api_route("/api/spider/ehentai", methods=["POST", "OPTIONS"], response_class=JSONResponse)
async def api_spider_ehentai(request: Request):
    '''start spider ehentai'''

    # handle main logic
    if request.method == "OPTIONS" or request.method == "POST":
        jsonData = await request.json()
        url = jsonData["url"]
        
        spider_id = get_sha256(url)
        if motor.atlas_manager.is_atlas_exists(spider_id):
            result = jsonable_encoder({"ret":False, "msg": "atlas is already exist"})
            return JSONResponse(content=result, headers={"Content-Type": "application/json"})
        
        def after_done(title, folder_path, imagenames):
            '''insert atlas to database'''

            motor.atlas_manager._db.insert_atlas(spider_id, title, folder_path, imagenames, url)

        success, message = run_ehspider(url, spider_id, folder_gallery, after_done)
        result = jsonable_encoder({"ret":success, "msg": message})
        return JSONResponse(content=result, headers={"Content-Type": "application/json"})
    
    return JSONResponse(content={"ret":False, "msg":f"invalid method:{request.method}"}, headers={"Content-Type": "application/json"})

if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
