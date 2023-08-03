from google.auth.transport import requests
from google.oauth2 import service_account
import os

class HealthcareApi:
    def __init__(self, project_id, location):
        self.credentials = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        self.scoped_credentials = self.credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
        self.session = requests.AuthorizedSession(self.scoped_credentials)
        self.base_url = "https://healthcare.googleapis.com/v1"
        self.url = f"{self.base_url}/projects/{project_id}/locations/{location}"
        self.header = {"Content-Type": "application/fhir+json;charset=utf-8"}


    def create(self, dataset_id: str, fhir_store_id: str, resource: str, payload: dict) -> None:

        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"

        response = self.session.post(resource_path, headers=self.header, json=payload)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Created Patient resource with ID {return_payload['id']}")

        return {'response': response, 'payload': return_payload}


    def update(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str, payload: dict) -> dict:

        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"

        response = self.session.put(resource_path, headers=self.header, json=payload)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Updated {resource} resource with ID {resource_id}")    

        return {'response': response, 'payload': return_payload}

    
    def read(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str) -> dict:

        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"
        
        response = self.session.get(resource_path, headers=self.header)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Got contents of {resource} resource with ID {resource_id}:\n")

        return {'response': response, 'payload': return_payload}

    
    def read_lastupdated(self, dataset_id: str, fhir_store_id: str, resource: str, since: dict) -> dict:
        '''  
        since: '2023-08-01T03:00:00.000Z'
        '''

        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"
        resource_path += f"?_lastUpdated=gt{since}"
        
        response = self.session.get(resource_path, headers=self.header)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Got {return_payload['total']} entries from {resource}")

        return {'response': response, 'payload': return_payload}


    def delete(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str) -> None:
  
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"
        
        response = self.session.delete(resource_path, headers=self.header)
        response.raise_for_status()

        print(f"Deleted {resource} resource with ID {resource_id}.")

        return {'response': response}
    