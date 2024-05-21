import pymupdf
from langchain_core.documents import Document
from typing import List
import requests
from PIL import Image
import os
import imghdr
from chatapi.LLMConnection import LLMConnection
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import RetrievalQA
import json
from fpdf import FPDF
import sqlite3


##----------------#
# from fastapi import  Depends
# import sqlite3


# def get_db():
#     db = sqlite3.connect("C:/Users/gowrishankar.j/Desktop/aiml/lyfngo_ai_bot/database.db", check_same_thread=False)
#     try:
#         yield db
#     finally:
#         db.close()
##----------------#




class PdfExtractor:
    def __init__(self, pdf_path:str, sql_lite):
        self.pdf_path = pdf_path
        self.pdf_file = pymupdf.open(pdf_path)
        self.sql_lite = sql_lite

    def get_text_from_pdf(self) -> List[Document]:
        documents = []
        for page in self.pdf_file:
            document = page.get_text()
            if len(document) == 0:
                content = page.get_textpage_ocr(language='eng', dpi=100, full=False, tessdata="/usr/share/tesseract-ocr/4.00/tessdata")
                document= content.extractText()
            else:
                document = page.get_text()
            self.sql_lite.query_exec((document, page.number,"table", None, None))
            documents.append(Document(page_content=document,  metadata={'source': self.pdf_path, 'page': page.number}))
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
        return text_splitter.split_documents(documents)
            
    
                    
                    
                    
def image_to_pdf(image_path:str, pdf_path):
    pdf = FPDF()
    image_list = ["./test.jpeg"]  # List of image filenames
    for image in image_list:
        pdf.add_page()
        pdf.image(image, x=10, y=10, w=200, h=150)  # Adjust coordinates and size
    pdf.output("output.pdf", "F")  
    
    


class S3ImageToPDFConverter:
    def __init__(self, url:str):
        self.url = url

    def download_file(self, path):
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            return path
        else:
            raise Exception(f"Failed to download the file: Status code {response.status_code}")

    # def convert_imageimage_list = ["./test.jpeg"]_to_pdf(self, image_path, pdf_path):
    #     with Image.open(image_path) as img:
    #         img.convert('RGB').save(pdf_path, 'PDF')
            
    def convert_image_to_pdf(self, image_path, pdf_path):
        pdf = FPDF()
        image_list = [image_path]  # List of image filenames
        for image in image_list:
            pdf.add_page()
            pdf.image(image, x=10, y=10, w=200, h=150)
        pdf_path = pdf_path.split(".")[0]
        pdf_path = f"{pdf_path}.pdf"
        pdf.output(pdf_path, "F")  
        return pdf_path

    def delete_file(self, path):
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted file: {path}")
        else:
            print(f"File not found: {path}")

    def process_file_to_pdf(self, download_path:str, pdf_path:str):

        try:
            self.download_file(download_path)
            file_type = imghdr.what(download_path)
            if file_type:
                pdf_path = self.convert_image_to_pdf(download_path, pdf_path)
                self.delete_file(download_path)
                print(f"Image converted to PDF and saved at: {pdf_path}")
                return pdf_path
            else:
                with open(download_path, 'rb') as f:
                    if f.read(4) == b'%PDF':
                        return download_path
                    else:
                        print("The downloaded file is neither an image nor a PDF.")
                        self.delete_file(download_path)
                        return None
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"An error occurred: {e}")
            return None


class PDFRAG:
    def __init__(self, documents: List[Document], llmconnection: LLMConnection, collection_name: str, sql_lite):
        self.documents = documents
        self.llmconnection = llmconnection
        self.collection_name = collection_name
        self.sql_lite=sql_lite
        
    
    def vector_db_insert(self):
        self.llmconnection.update_collection_name(self.collection_name)
        hf = HuggingFaceEmbeddings(
        model_name=self.llmconnection.retriverModel.embeddings.model,
        model_kwargs=self.llmconnection.retriverModel.embeddings.model_kwargs,
        encode_kwargs=self.llmconnection.retriverModel.embeddings.encode_kwargs
        )
        
        connection_args={
                "host": self.llmconnection.retriverModel.vector_db.host,
                "port": self.llmconnection.retriverModel.vector_db.port,
            }
        print(connection_args, self.collection_name)
        #embeddings = OpenAIEmbeddings()
        vector_store = self.llmconnection.vector_db.from_documents(
            self.documents,
            embedding=hf,
            collection_name=self.collection_name,
            connection_args=connection_args
        )

    def rag(self):
        retriever = self.llmconnection.retriever

        

        template = self.llmconnection.llmModel.prompt
        print(template)

        rag_prompt = PromptTemplate.from_template(template)

        qa_chain = RetrievalQA.from_chain_type(
                llm=self.llmconnection.llm,
                retriever=retriever, chain_type="stuff",
                # chain_type_kwargs=chain_type_kwargs,
                return_source_documents=False)

        # response = qa_chain("list the blood report parameters as key value pairs formatted as JSON")
        # print("response>@@@@$$$$$",type(response),response)
        #----------------#
        
         # ONE COLUMN VALUE
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('SELECT test_parameter FROM csv_data')
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
        print("col_data",col_data)
        flat_list = []
        for sublist in col_data:
            for element in sublist:
                flat_list.append(element)
        print(flat_list)
        # out_ans_to_json = "Give above results as a json Format"
        # flat_list.append(out_ans_to_json)
        cursor.close()
        connection.close()
        srch_llm_out_to_json = []
        for srch_llm in flat_list: 
            f_str = f"what is my {srch_llm} level"
            response_one = qa_chain(f_str)
            srch_llm_out_to_json.append(response_one)
            print("response_one>*******",type(response_one),response_one)
            
            # f_str = f"what is my {srch_llm} level"
            # print("srch_llm",srch_llm)
            # if out_ans_to_json not in [f_str]:  
            # # if f_str.startswith("what", 0, 4):  
            #     response_one = qa_chain(f_str)
            #     print("response_one>*******",type(response_one),response_one)
            # if out_ans_to_json == srch_llm:
            # # elif srch_llm == out_ans_to_json:
            #     print("else path")
            #     final_response = qa_chain(srch_llm)
            #     print("final_response>*******",type(final_response),final_response)
            #     srch_llm_out_to_json.append(final_response)
            #     self.sql_lite.query_exec((None, None,"rage",template ,json.dumps(final_response)))
            #     # break
        print("srch_llm_out_to_json",srch_llm_out_to_json)
        with open("C:/Users/gowrishankar.j/Desktop/aiml/lyfngo_ai_bot/routes/json_file.json", "w") as file:
            json.dump(srch_llm_out_to_json,file)
        print("succ created json file")
        
        
        
        #----------------#
        self.sql_lite.query_exec((None, None,"rage",template ,json.dumps(srch_llm_out_to_json)))



# def has_collection(collection_name: str) -> bool:
#     try:
#         Collection(name=collection_name)
#         return True
#     except Exception as e:
#         return False

# # Endpoint to check and delete a collection

# def check_and_delete_collection(config_data):
#     connections.connect(host=config_data.milvusdata.host, port=config_data.milvusdata.port, alias='default')
#     if has_collection(config_data.milvusdata.collection_name):
#         collection_name =config_data.milvusdata.collection_name
#         Collection(name=collection_name).drop()
#         return {"message": f"Collection '{collection_name}' found and deleted."}
#     else:
#         return {"message": f"Collection '{collection_name}' not found."}