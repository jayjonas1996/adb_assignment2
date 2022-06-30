
import os, re
import pandas as pd
from azure.storage.blob import BlobServiceClient

class CloudStorage:
    container_name = 'textfiles'
    container = "https://jknadbassignment1.blob.core.windows.net/textfiles/"

    def __init__(self):
        pass

    def upload(self, file, name):
        containerName = "textfiles"
        blobName = name

        blobService = BlobServiceClient.from_connection_string(os.environ['BLOB_CONNECTION_STRING'])
        blob_client = blobService.get_blob_client(container=containerName, blob=blobName)

        try:
            blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)
        except Exception as e:
            print(e)
    
    def place(self, local_path, file_name):
        blob_service_client = BlobServiceClient.from_connection_string(os.environ['BLOB_CONNECTION_STRING'])
        container_client = blob_service_client.get_container_client(self.container_name)
        container_client.list_blobs()
        blob_client = container_client.get_blob_client(file_name)

        try:
            with open(local_path, "rb") as data:
                    blob_client.upload_blob(data, blob_type="BlockBlob", overwrite=True)
        except Exception as e:
            print(e)
    
    def list_b(self):
        blob_service_client = BlobServiceClient.from_connection_string(os.environ['BLOB_CONNECTION_STRING'])
        container_client = blob_service_client.get_container_client(self.container_name)
        return container_client.list_blobs()

class NLP():
     
    def __init__(self):
        pass

    def process(self, data):
        text = data.read().lower().decode()
        text = re.sub(r'[^\w\s]', '', text) 
        a = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
        text = re.sub(r'( ' + r' | '.join(a) + r' )', ' ', text)
        return text
    
    def process_quiz5(self, data):
        text = data.read().lower().decode()
        text = re.sub(r'[^\w\s]', '', text)
        
        sw = []
        with open(os.getcwd() + '/files/spanish_stopwords.csv', 'r') as f:
            for i in f.readlines():
                if i:
                    sw.append(i[:-1])

        text = re.sub(r'( ' + r' | '.join(sw) + r' )', ' ', text)
        return text
