import msal
import requests
class GraphAPIClient:
    def __init__(self, client_id,client_secret,tenant_id):
        self.client_id =  client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def acess_token(self):
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(self.client_id, authority=authority, client_credential=self.client_secret)
        scope = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scope)
        
        if "access_token" in result:
            self.token = result['access_token']
        else:
            self.token=result.get("error")
        return(self.token)
    
    def update_fields(self, site_id, list_id, fields):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = f"{self.base_url}/sites/{site_id}/lists/{list_id}"
        body = {
            'fields': fields
        }
        response = requests.patch(url, headers=self.headers, json=body)
        return response.json()
 
    def create_item(self,site_id, list_id, fields):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items"
        body = {
            'fields': fields
        }
        response = requests.post(url, headers=self.headers,json=body)
        return response.json()
    
    def delete_item(self,site_id, list_id,item_id):
        self.item_id = item_id
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items/{self.item_id}"
        response = requests.delete(url, headers=self.headers)
        return response
    
    def get_item(self,site_id, list_id,item_id):
        self.item_id = item_id
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items/{item_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_items(self,site_id, list_id,expand):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        if expand == '*':
            url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items?expand=fields"    
        elif expand == None:
            url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items"
        else:
            url = f"{self.base_url}/sites/{site_id}/lists/{list_id}/items?expand=fields(select={expand})"
        response = requests.get(url, headers=self.headers)
        return response.json()