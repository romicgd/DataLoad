import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the environment variables
domain_base: str = os.getenv("domain_base")
relative_site_url: str = os.getenv("relative_site_url")
site_url: str = domain_base + relative_site_url
client_id: str = os.getenv("client_id")
client_secret: str = os.getenv("client_secret")

# Create a client context
ctx = ClientContext(site_url).with_credentials(
    ClientCredential(client_id, client_secret)
)


def download_file(sp_file, local_folder):
    file_name = sp_file.properties["Name"]
    local_file_path = os.path.join(local_folder, file_name)
    with open(local_file_path, "wb") as local_file:
        sp_file.download(local_file)
        ctx.execute_query()
    print(f"Downloaded: {local_file_path}")


def download_folder(sp_folder, local_folder):
    os.makedirs(local_folder, exist_ok=True)
    folders = sp_folder.folders
    print(local_folder)
    ctx.load(folders)
    try:
        ctx.execute_query()
        for folder in folders:
            ServerRelativeUrl = folder.properties["ServerRelativeUrl"]
            sub_sp_folder = ctx.web.get_folder_by_server_relative_url(ServerRelativeUrl)
            folder_name = os.path.basename(ServerRelativeUrl)
            if folder_name == "Forms":
                continue
            download_folder(sub_sp_folder, os.path.join(local_folder, folder_name))
    except Exception as e:
        print(f"Error processing folders in {local_folder}: {e}")
    finally:
        files = sp_folder.files
        ctx.load(files)
        ctx.execute_query()
        for file in files:
            download_file(file, local_folder)


def main():
    library_name: str = os.getenv("library_name")
    target_folder_url: str = f"{relative_site_url}/{library_name}"
    sp_root_folder = ctx.web.get_folder_by_server_relative_url(target_folder_url)
    ctx.load(sp_root_folder)
    ctx.execute_query()
    data_folder = os.getenv("data_folder")
    download_folder(sp_root_folder, data_folder)


if __name__ == "__main__":
    main()
