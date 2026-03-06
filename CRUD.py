import requests

# Server address — update if the server IP changes
server_ip = "100.126.111.17:22500"

def fileUpload(user_name: str, file_path: str):
    """Upload an already-encrypted file to the server."""
    url = f"http://{server_ip}/upload/{user_name}"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f)}
        response = requests.post(url, files=files)
    print(f"[fileUpload] Status: {response.status_code} | Response: {response.json()}")

def vaultUpload(user_name: str, vault_path: str):
    """Upload the biometric vault to the server."""
    url = f"http://{server_ip}/registration/{user_name}"
    print(f"[vaultUpload] URL: {url}")
    with open(vault_path, "rb") as f:
        vault = {"vault": (vault_path, f)}
        response = requests.post(url, files=vault)
    print(f"[vaultUpload] Status: {response.status_code} | Response: {response.json()}")

def retrieveFile(user_name: str, file_name: str, dest_path: str):
    """Download an encrypted file from the server and save it to dest_path."""
    url = f"http://{server_ip}/return/{user_name}/{file_name}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, "wb") as f:
            f.write(response.content)
        print(f"[retrieveFile] Downloaded '{file_name}' successfully.")
        return True
    else:
        print(f"[retrieveFile] Failed: {response.status_code}")
        return False

def retrieveVault(user_name: str, dest_path: str):
    """Download the biometric vault for a user and save it to dest_path."""
    url = f"http://{server_ip}/returnVault/{user_name}/vault.pkl"
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, "wb") as f:
            f.write(response.content)
        print(f"[retrieveVault] Vault downloaded successfully.")
        return True
    else:
        print(f"[retrieveVault] Failed: {response.status_code}")
        return False

def listOfFiles(user_name: str):
    """Return a list of filenames stored on the server for the user, or [] on failure."""
    url = f"http://{server_ip}/files/{user_name}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            files = data if isinstance(data, list) else []
            return files
        except Exception as e:
            print(f"[listOfFiles] Parse error: {e}")
            return []
    else:
        print(f"[listOfFiles] Failed: {response.status_code}")
        return []
