import sqlite3
import boto3
import os
from botocore.exceptions import NoCredentialsError

class SQLiteDBHandler:
    def __init__(self, db_name, bucket_name, aws_access_key_id, aws_secret_access_key, key, region_name='us-east-1'):
        self.db_name = db_name
        self.bucket_name = bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.key=key
        self.s3_client = boto3.client('s3', 
                                      aws_access_key_id=self.aws_access_key_id,
                                      aws_secret_access_key=self.aws_secret_access_key,
                                      region_name=self.region_name)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        try:
            query = '''
                    CREATE TABLE IF NOT EXISTS ContentTable (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    page_number INTEGER,
                    type VARCHAR,
                    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    prompt_template TEXT,
                    answer TEXT
                )

            '''
            self.cursor.execute(query)
        except sqlite3.Error as e:
            print(e)

    def query_exec(self, data_tuple):
        try:
            sql_query = "INSERT INTO ContentTable (content, page_number, type, prompt_template, answer) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(sql_query, data_tuple)
            self.conn.commit()
        except sqlite3.Error as e:
            import traceback
            traceback.print_exc()

    
    def upload_to_s3(self):
        try:
            self.conn.close()  # Ensure data is saved and connection is closed before upload
            print("sdfsd", f"{os.getcwd()}/{self.db_name}", self.bucket_name, self.db_name, self.key)
            self.s3_client.upload_file(Filename=f"{os.getcwd()}/{self.db_name}", Bucket=self.bucket_name, Key=f"{self.key}/{self.db_name}")
            print(f'Successfully uploaded {self.db_name} to S3 bucket {self.bucket_name}')
            # self.delete_local_db_file()  
        except FileNotFoundError:
            print("The file was not found")
        except NoCredentialsError:
            print("Credentials not available")
        except Exception as e:
            print(f"An error occurred: {e}")

    def delete_local_db_file(self):
        """Deletes the local database file if it exists."""
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
            print(f"Successfully deleted the local database file: {self.db_name}")
        else:
            print(f"No local database file to delete: {self.db_name}")

    def __del__(self):
        if self.conn:
            self.conn.close()
            



