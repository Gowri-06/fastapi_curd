from fastapi import FastAPI, Request, UploadFile, File, Cookie
import shutil
app = FastAPI()
from fastapi.staticfiles import StaticFiles
from pypdf import PdfReader 
import json
from tabula import read_pdf
from tabulate import tabulate
# importing the library  
import tabula  
import camelot
import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Form
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse




app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

@app.get("/hello/{name}/", response_class=HTMLResponse)
async def hello(request: Request,name:str):
   print(request.method)
   return templates.TemplateResponse("hello.html", {"request": request,"name":name})
  
@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
   return templates.TemplateResponse("login.html", {"request": request})

@app.get("/upload/", response_class=HTMLResponse)
async def upload(request: Request):
   return templates.TemplateResponse("uploadfile.html", {"request": request})


@app.get("/upload/", response_class=HTMLResponse)
async def upload(request: Request):
   return templates.TemplateResponse("uploadfile.html", {"request": request})


@app.post("/uploader/")
async def create_upload_file(file: UploadFile = File(...)):
   with open("destination.png", "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)
   return {"filename": file.filename}

# @app.post("/submit/")
# async def submit(nm: str = Form(...), pwd: str = Form(...)):
#    return {"username": nm}

from pydantic import BaseModel

class User(BaseModel):
   username:str
   password:str


 

@app.post("/submit/", response_model=User)
async def submit(nm: str = Form(...), pwd: str = Form(...)):
   print("User>>>>")
   a = User(username=nm, password=pwd) 
   print(type(a))
  #  _book = Book(title=book.title, author=book.author,publication_year=book.publication_year)
  #  db.add(a)
  #  db.commit()
  #  db.refresh(a)
   return a
  #  return User(username=nm, password=pwd)

@app.post("/cookie/")
def create_cookie():
   content = {"message": "cookie set"}
   response = JSONResponse(content=content)
   response.set_cookie(key="username", value="admin")
   return response

@app.get("/readcookie/")
async def read_cookie(username: str = Cookie(None)):
   return {"username": username}


@app.get("/hi/")
async def index():
  #  importing required modules 
  print("dd")
  # creating a pdf reader object 
  reader = PdfReader("C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/BloodTest-2022-Dec.pdf") 
  print(reader)
  # printing number of pages in pdf file 
  print(len(reader.pages)) 
  # # getting a specific page from the pdf file 
  page = reader.pages
  print(page)
  listdta = []
  page_no = 0
  text = 0
  dict1 = {}
  for i in page:
      a = i.extract_text()
      rem_char = a.replace("\n","")
      print("rem_char",rem_char)
      ditc2 = {}
      page_no += 1
      text += 1
      new_key = "key" + str(text)
      print("extracted_text",a)
      conversion = "pageno: " + str(page_no) + " " + a + " "
      conversion2 =   a 
      dict1.update({str(page_no):page_no,new_key:rem_char})
      listdta.append(conversion)
  print("listdta",listdta)
  print("key",dict1)
  with open("BloodTestcharremovedsss.json", "w") as f:
     json.dump(dict1, f)
  # json_data = json.dumps(dict1)
  # print(json_data)

  # with open("C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/BloodTest-2022-Dec.txt", "w",encoding='utf8') as file:
  #    for j in listdta:
  #       file.write(j)

  # print("file saved")
# # extracting text from page 
  # text = page.extract_text() 
  # print(text) 

  return {"message": "Hello world"}

@app.get("/test/")
async def bye():
  # address of the file  
  # myfile = 'C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/data_tables_sample.pdf'  
  myfile = 'C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/BloodTest-2022-Dec.pdf'  
  print("myfile",myfile)
  # using the read_pdf() function  
  mytable = tabula.read_pdf(myfile)  
  # mytable2 = tabula.read_pdf(myfile, pages = 2,multiple_tables = True)  
  print("mytable",type(mytable),len(mytable))
  i = 0
  table_list = []
  dta_frame = []
  # creating a pdf reader object 
  reader = PdfReader("C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/BloodTest-2022-Dec.pdf") 
  print(reader)
  # printing number of pages in pdf file 
  print(len(reader.pages)) 
  no_of_pages = len(reader.pages) 
  for table in mytable:
    print(type(table),len(mytable))
    print("mytable",len(mytable))
    i += 1
    print("i>>>>>>>",i)
    print("tablenum",table)
    # json_str = table.to_json(orient="records")
    # json_str = table.to_json('BloodTest-2022-Dec-table.json')
    # json_str = table.to_csv('output1.csv',encoding='utf8')
    print("json_str")
    table_list.append(table.to_json())
    print("table_list",table_list)
    # json_str = table_list.to_json(orient="records")
    with open("dataframesalltables.json", "w") as f:
       json.dump(table_list, f)
       
  

    # print(json_str)

    # result = pd.concat(mytable)
    # print(result)
    # json_str = result.to_csv('outputsucc.csv',encoding='utf8')
    # print("sss")


  # for table in mytable2:
  #   print(type(table))
  #   # json_str = table.to_json(orient="records")
  #   json_str = table.to_json('output2.json')
  #   print("json_str")
  #   print(json_str)
  # print("@@@")



  # print(tabulate(mytable))
  # print(">??????????",mytable[5])  
  # extract all the tables in the PDF file
  # abc = camelot.read_pdf(myfile) #address of file location
  # for table in abc:
  #   print(table.df)
  # print the first table as Pandas DataFrame
  # print(abc[0].df)
  return "test message"








