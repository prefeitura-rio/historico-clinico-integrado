from google.auth.transport import requests
from google.oauth2 import service_account
import os

class HealthcareApi:
    """
    This class provides the basic methods for interacting with the Google Healthcare API.
    Based on examples from:
        https://github.com/GoogleCloudPlatform/python-docs-samples/tree/3aa00a7549571b3a6ce8333d857226011e74a9be/healthcare/api-client/v1/fhir
        https://github.com/GoogleCloudPlatform/python-docs-samples/tree/3aa00a7549571b3a6ce8333d857226011e74a9be/healthcare/api-client/v1beta1/fhir
    """
    def __init__(self, project_id, location):
        self.credentials = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        self.scoped_credentials = self.credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
        self.session = requests.AuthorizedSession(self.scoped_credentials)
        self.base_url = "https://healthcare.googleapis.com/v1"
        self.url = f"{self.base_url}/projects/{project_id}/locations/{location}"
        self.header = {"Content-Type": "application/fhir+json;charset=utf-8"}


    def create(self, dataset_id: str, fhir_store_id: str, resource: str, payload: dict) -> None:
        """Create a new resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"

        response = self.session.post(resource_path, headers=self.header, json=payload)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Created Patient resource with ID {return_payload['id']}")

        return {'response': response.status_code, 'payload': return_payload}


    def update(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str, payload: dict) -> dict:
        """Update an existing resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"

        response = self.session.put(resource_path, headers=self.header, json=payload)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Updated {resource} resource with ID {resource_id}")    

        return {'response': response.status_code, 'payload': return_payload}

    
    def read(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str) -> dict:
        """Read the contents of a specific resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"
        
        response = self.session.get(resource_path, headers=self.header)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Got contents of {resource} resource with ID {resource_id}:\n")

        return {'response': response.status_code, 'payload': return_payload}
   

    def read_conditional(self, dataset_id: str, fhir_store_id: str, resource: str, condition: str) -> dict:
        """Read the entries from a resource in the FHIR store that were last updated after a specific date and time"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"
        resource_path += f"?{condition}"
        
        response = self.session.get(resource_path, headers=self.header)
        response.raise_for_status()

        return_payload = response.json()

        print(f"Got {return_payload['total']} entries from {resource}")

        return {'response': response.status_code, 'payload': return_payload}


    def delete(self, dataset_id: str, fhir_store_id: str, resource: str, resource_id: str) -> None:
        """Delete a resource from the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"
        
        response = self.session.delete(resource_path, headers=self.header)
        response.raise_for_status()

        print(f"Deleted {resource} resource with ID {resource_id}.")

        return {'response': response.status_code}


class FastCRUD(HealthcareApi):
    """The  FastCRUD  class is a subclass of HealthcareApi that provides additional convenience methods for most common CRUD actions."""
    def __init__(self, project_id, location):
        super().__init__(project_id, location)

    def read_lastupdated(self, dataset_id: str, fhir_store_id: str, resource: str, since: str) -> dict:
        """Read the entries from a resource in the FHIR store that were last updated after a specific date and time"""
        parameter = f"_lastUpdated=gt{since}"
        return self.read_conditional(dataset_id, fhir_store_id, resource, parameter)
    
    def read_patient(self, dataset_id: str, fhir_store_id: str, cpf: str):
        """Read the entries from Patient resource in the FHIR store based on tax id (CPF)"""
        parameter = f"identifier=https://rnds-fhir.saude.gov.br/NamingSystem/cpf|{cpf}"
        return self.read_conditional(dataset_id, fhir_store_id, 'Patient', parameter)