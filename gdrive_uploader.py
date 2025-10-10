# gdrive_uploader.py
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_to_drive(file_path, folder_id="1-yBe6wqI_DXO1b7GCLk7ivkzuWi5UySA"):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.json")

    if gauth.credentials is None:
        # Jalankan sekali di server lokal untuk login
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.json")

    drive = GoogleDrive(gauth)
    file_name = file_path.split("/")[-1]

    file = drive.CreateFile({
        "title": file_name,
        "parents": [{"id": folder_id}] if folder_id else []
    })
    file.SetContentFile(file_path)
    file.Upload()
    file.InsertPermission({
        "type": "anyone",
        "value": "anyone",
        "role": "reader"
    })
    print(f"✅ File uploaded to Drive: {file['alternateLink']}")
    return file['alternateLink']
