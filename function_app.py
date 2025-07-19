import logging
import os
from datetime import datetime
 
import azure.functions as func
import azure.durable_functions as df
from azure.storage.blob import BlobServiceClient
from PIL import Image
import io
import pymssql
 
# ✅ Secure: Read storage connection string from env
blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("AzureWebJobsStorage"))
 
# ✅ Initialize Durable Function app
my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
 
# ✅ Trigger: Blob upload starts orchestration
@my_app.blob_trigger(arg_name="myblob", path="images-input/{name}", connection="AzureWebJobsStorage")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    blob_name = myblob.name.split("/")[-1]
 
    # ✅ Optional: Skip unsupported file types
    if not blob_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        logging.warning(f"Unsupported file type skipped: {blob_name}")
        return
 
    logging.info(f"Blob trigger processed blob: Name={myblob.name}, Size={myblob.length} bytes")
    await client.start_new("orchestrator", client_input=blob_name)
 
# ✅ Orchestrator: Coordinates metadata extraction and storage
@my_app.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    blob_name = context.get_input()
 
    retry_options = df.RetryOptions(first_retry_interval_in_milliseconds=5000, max_number_of_attempts=3)
 
    metadata = yield context.call_activity_with_retry("extract_metadata", retry_options, blob_name)
    yield context.call_activity_with_retry("store_metadata", retry_options, metadata)
 
    return f"Metadata processed and stored for {blob_name}"
 
# ✅ Activity: Extract image metadata
@my_app.activity_trigger(input_name='blobName')
def extract_metadata(blobName):
    logging.info(f"Extracting metadata for {blobName}")
    container_client = blob_service_client.get_container_client("images-input")
    blob_client = container_client.get_blob_client(blobName)
    blob_bytes = blob_client.download_blob().readall()
 
    with Image.open(io.BytesIO(blob_bytes)) as img:
        metadata = {
            "FileName": blobName,
            "FileSizeKB": round(len(blob_bytes) / 1024, 2),
            "Width": img.width,
            "Height": img.height,
            "Format": img.format
        }
 
    logging.info(f"Extracted metadata: {metadata}")
    return metadata
 
# ✅ Activity: Store metadata securely using env vars
@my_app.activity_trigger(input_name='metadata')
def store_metadata(metadata):
    logging.info(f"Storing metadata in SQL DB: {metadata}")
    conn = None
    cursor = None
    try:
        conn = pymssql.connect(
            server=os.environ.get("SQL_SERVER"),
            user=os.environ.get("SQL_USER"),
            password=os.environ.get("SQL_PASSWORD"),
            database=os.environ.get("SQL_DB"),
            port=1433
        )
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, Format)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            metadata["FileName"],
            metadata["FileSizeKB"],
            metadata["Width"],
            metadata["Height"],
            metadata["Format"]
        ))
        conn.commit()
        logging.info("Metadata stored successfully.")
    except Exception as e:
        logging.error(f"Failed to store metadata: {e}", exc_info=True)
        raise
    finally:
        cursor.close()
        conn.close()
 
    return "Metadata stored successfully."
