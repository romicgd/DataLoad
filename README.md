# SharePoint Online Data Loader

This project is a Python script to download files and folders from a SharePoint Online site to a local directory.

## Configuration

1. Create App registration:

Create App registration in MS Entra and note client_id and client secret

2. Configure required aplication permissions
https://yourtenant.sharepoint.com/sites/yoursite/_layouts/15/appinv.aspx

Specify your site client_id

```xml
<AppPermissionRequests AllowAppOnlyPolicy="true">
  <AppPermissionRequest Scope="http://sharepoint/content/sitecollection/web" Right="Read" />
</AppPermissionRequests>
```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a .env file in the root directory of the project and add your SharePoint credentials:

    ```env
    site_url=https://yourtenant.sharepoint.com/sites/yoursite
    client_id=your-client-id
    client_secret=your-client-secret
    ```