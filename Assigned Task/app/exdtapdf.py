# importing required modules 
from pypdf import PdfReader 
print("dd")
# creating a pdf reader object 
reader = PdfReader("C:/Users/HP/Desktop/fastapi_curd/Assigned Task/app/Sample-pdf.pdf") 

# printing number of pages in pdf file 
print(len(reader.pages)) 

# # getting a specific page from the pdf file 
page = reader.pages
print(page)
for i in page:
    a = i.extract_text()
    print(a)



# # extracting text from page 
# text = page.extract_text() 
# print(text) 


