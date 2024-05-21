from fastapi import APIRouter
import os
from chatapi.LLMConnection import LLMConnection
from pydantic  import BaseModel
from utils.pdf_extractor import (S3ImageToPDFConverter,
                                 PdfExtractor,
                                 PDFRAG)
from utils.sql_lite import SQLiteDBHandler
from dotenv import load_dotenv
import random
import string
from fastapi import FastAPI
from apiv1.model import SessionLocal
import sqlite3


load_dotenv()



def random_char():
       return ''.join(random.choice(string.ascii_letters) for x in range(10))




file_extractor = APIRouter()



class FileExtractorRequest(BaseModel):
    s3_url: str
    client_id: str
    


async def split_s3_path(s3_path):
    parts = s3_path.split('/')
    s3_bucket_name = parts[2].split('.')[0] 
    s3_key = '/'.join(parts[3:-1])
    file_name = parts[-1].split(".")[0]
    file_name_with_extension =  parts[-1]
    return s3_bucket_name, s3_key, file_name, file_name_with_extension
    
    
    
    
    



def extract_upload(s3_url:str, llm_data:LLMConnection, collection_name:str, sql_lite, file_name_with_extension) -> bool:
    try:
        converter = S3ImageToPDFConverter(url=s3_url)
        file_path = converter.process_file_to_pdf(download_path=f"{os.getcwd()}/file/{file_name_with_extension}", pdf_path=f"{os.getcwd()}/file/{file_name_with_extension}.pdf")
        if not file_path:
            return False
        spliter_text = PdfExtractor(file_path, sql_lite).get_text_from_pdf()
        rag_config = PDFRAG(spliter_text, llmconnection=llm_data, collection_name=random_char(), sql_lite=sql_lite)
        rag_config.vector_db_insert()
        rag_config.rag()
        
        
    except:
        import traceback
        traceback.print_exc()

@file_extractor.post("/file-extractor")
async def file_extractor_api(request_json: FileExtractorRequest):
    llm_data = LLMConnection(request_json.client_id, "blood_test")
    bucket_name, path, file_name, file_name_with_extension = await split_s3_path(request_json.s3_url)
    
    sql_lite = SQLiteDBHandler(db_name=f"{file_name}.sqlite", bucket_name=bucket_name, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), key=path, region_name="ap-south-1")
    sql_lite.create_table()
    extract_upload(s3_url=request_json.s3_url, llm_data=llm_data, collection_name=file_name, sql_lite=sql_lite, file_name_with_extension=file_name_with_extension)
    sql_lite.upload_to_s3()
    

#---------------------------------------#

from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import csv

app = FastAPI()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Dependency to get DB connection


def get_db():
    db = sqlite3.connect("C:/Users/gowrishankar.j/Desktop/aiml/lyfngo_ai_bot/database.db", check_same_thread=False)
    try:
        yield db
    finally:
        db.close()
   
@file_extractor.get("/csv-data-to-table/")
# async def llm_data_to_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
# async def llm_data_to_json(db: Session = Depends(get_db)):
async def llm_data_to_json(db: sqlite3.Connection = Depends(get_db)):
    print("check")
    # Read the data from the CSV file
    list = []
    # Connect to the SQLite database
    # conn = sqlite3.connect("C:/Users/gowrishankar.j/Desktop/aiml/lyfngo_ai_bot/database.db")
    cursor = db.cursor()

    # Create the table if it doesn't exist
    cursor.execute(
    """CREATE TABLE IF NOT EXISTS csv_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_parameter TEXT,
        uni_of_measurement TEXT,
        approximate_normal_range TEXT,
        notes_on_abnormal_values TEXT,
        prompt TEXT
    )"""
)
     # age INTEGER

    
    
    with open("C:/Users/gowrishankar.j/Desktop/aiml/lyfngo_ai_bot/routes/AI_ML-Project - Common_Blood_Test_Parameters.csv", "r") as f:
        reader = csv.reader(f)
        print(reader)
        # print(len(reader))
        next(reader)  # Skip the header row

        # Insert each row into the database
        for row in reader:
            print(row)
            list.append(row)
            cursor.execute("""INSERT INTO csv_data (test_parameter, uni_of_measurement, approximate_normal_range, notes_on_abnormal_values, prompt) VALUES (?, ?, ?, ?, ?)""", row)
            
            # Commit the changes and close the connection
            db.commit()
            # conn.commit()
            # conn.close()
        cursor.close()  # Close cursor after all operations are done
            # Close the connection after cursor is closed
        db.close()

    print(len(list))
    return {"message": "CSV data uploaded successfully"}




   
@file_extractor.get("/csv-table-data-show/")
# async def llm_data_to_json(file: UploadFile = File(...), db: Session = Depends(get_db)):
# async def llm_data_to_json(db: Session = Depends(get_db)):
async def csv_table_data(db: sqlite3.Connection = Depends(get_db)):
    # Create a connection object
    # conn = sqlite3.connect('database.db')

    # Create a cursor object
    cursor = db.cursor()
    list1  = []
    # Execute a query to select all records from the 'customers' table
    cursor.execute('SELECT * FROM csv_data')
    # cursor.execute('DELETE FROM csv_data')

    # Fetch all records from the cursor
    records = cursor.fetchall()
    print("records",records)
    # Print the records
    for record in records:
        print(type(record))
        print(record)
        list1.append(record)
    print(len(list1))
    
    # ONE COLUMN VALUE
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT prompt FROM csv_data')
    ext_col_data = cursor.fetchall()
    col_data = []
    for record in ext_col_data:
        print("ext_col_data")
        print(type(record))
        print(record)
        # list1.append(record)
        # print(len(list1))
        print()
        col_data.append(record)
    cursor.close()
    connection.close()
    
    print("col_data",col_data)
    flat_list = []
    for sublist in col_data:
        for element in sublist:
            flat_list.append(element)
    print(flat_list)
    
    # db.commit()
    # Close the connection
    db.close()
    return flat_list




# data = [{
# "Hemoglobin (Hb)":{
# "Unit of Measurement":"g/dL",
# "Approximate Normal Range":"13.8 to 17.2 g/dL (men), 12.1 to 15.1 g/dL (women)",
# "Notes on Abnormal Values":"Low: Anemia; High: Polycythemia"
# },
# "Hematocrit (Hct)":{
# "Unit of Measurement":"%",
# "Approximate Normal Range":"41% to 50% (men), 36% to 44% (women)",
# "Notes on Abnormal Values":"Low: Anemia; High: Dehydration"
# }
# }
# ]

    
    
    
        
    
#---------------------------------------#
    
    

    



    
    
    