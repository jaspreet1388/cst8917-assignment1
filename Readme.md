## CST8917 Assignment 1: Durable Workflow for Image Metadata Processing


### Objective

Build a serverless image metadata processing pipeline using Azure Durable Functions in Python. This assignment challenges you to use blob triggers, activity functions, and output bindings, and to deploy a complete solution to Azure. You'll simulate a real-world event-driven system.

### Scenario

A fictional content moderation team wants to analyze the metadata of user-uploaded images. Your Durable Functions app should:

Automatically trigger when a new image is uploaded to blob storage.
Extract metadata (e.g., file size, format, dimensions).
Store the metadata in an Azure SQL Database.
Workflow Requirements


## Setup Instructions

###  Prerequisites

- Python 3.10+
- Azure CLI
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- `func` and `az` CLI access
- Azure resources:
  - Storage account with `images-input` container
  - SQL Server & Database (`ImageMetadata` table must exist)

### Step 1: Blob Trigger (Client Function)

Create a blob-triggered function that starts the orchestration.
The blob container (e.g., images-input) should accept .jpg, .png, or .gif images.


### 2. Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

func start
```
### local settings json file 
``` json 
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<Your_Connection_String>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "SQL_SERVER": "<server>.database.windows.net",
    "SQL_USER": "<username>",
    "SQL_PASSWORD": "<password>",
    "SQL_DB": "<database>"
  }
}
```

### sql schema
``` sql
CREATE TABLE ImageMetadata (
  Id INT IDENTITY(1,1) PRIMARY KEY,
  FileName NVARCHAR(255),
  FileSizeKB FLOAT,
  Width INT,
  Height INT,
  Format NVARCHAR(50),
  Timestamp DATETIME DEFAULT GETDATE()
);

```
### Step 2: Orchestrator Function

The orchestrator should:
Call an activity function to extract metadata from the image.
Call a second activity function to store that metadata in Azure SQL DB via output binding.

### Step 3: Activity Function – Extract Metadata

Extract the following from each image:
File name
File size in KB
Width and height (in pixels)
Image format (e.g., JPEG, PNG)
Step 4: Activity Function – Store Metadata

Use Azure SQL output binding to store the image metadata.
## Screen shots:
<img width="2782" height="1524" alt="image" src="https://github.com/user-attachments/assets/a9fc0dda-b000-4a37-a441-a2b1948d7960" />

<img width="2930" height="954" alt="image" src="https://github.com/user-attachments/assets/18c4aa59-1cec-40a2-b1a5-77101904f20d" />

<img width="2930" height="1430" alt="image" src="https://github.com/user-attachments/assets/2971b3f0-71ac-4469-a6b7-7d6c2e9775f8" />

<img width="1462" height="747" alt="image" src="https://github.com/user-attachments/assets/b1cf9be3-31bc-44df-8050-0f47897868d8" />





Please find the tutorial link : https://youtu.be/dSh6wxZkE58
