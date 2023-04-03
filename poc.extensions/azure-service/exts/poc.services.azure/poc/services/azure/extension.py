import omni.ext
from omni.services.core import main

import sys
for p in sys.path:
    print(p)

from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient

# Paste in azure storage account connection string here
ACCT_CONN_STR = ""

def hello_azure_blob():
    try:
        blob_service = BlobServiceClient.from_connection_string(ACCT_CONN_STR)
        print(f"hello azure blob: {blob_service.account_name}")
        return f"hello azure blob: {blob_service.account_name}"
    except ValueError as e:
        print("Connection string is invalid.")
        raise e
    except Exception as e:
        print("Failed to Connect to Azure Storage Account.")
        raise e


def hello_azure_table():
    try:
        table_service = TableServiceClient.from_connection_string(ACCT_CONN_STR)
        print(f"hello azure table: {table_service.account_name}")
        return f"hello azure table: {table_service.account_name}"
    except ValueError as e:
        print("Connection string is invalid.")
        raise e
    except Exception as e:
        print("Failed to Connect to Azure Storage Account.")
        raise e
    

class PocServicesAzureExtension(omni.ext.IExt):

    def on_startup(self, ext_id):
        main.register_endpoint("get", "/hello_azure_blob", hello_azure_blob)
        main.register_endpoint("get", "/hello_azure_table", hello_azure_table)

    def on_shutdown(self):
        main.deregister_endpoint("get", "/hello_azure_blob")
        main.deregister_endpoint("get", "/hello_azure_table")
