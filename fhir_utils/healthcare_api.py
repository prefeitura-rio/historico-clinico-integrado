# -*- coding: utf-8 -*-
from google.auth.transport import requests
from google.oauth2 import service_account
import os


class HealthcareApi:
    """
    This class provides the basic methods for interacting with FHIR resources in the Google Healthcare API.
    Reference:
        https://cloud.google.com/healthcare-api/docs/reference/rest
    """

    def __init__(self, project_id, location):
        self.credentials = service_account.Credentials.from_service_account_file(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        self.scoped_credentials = self.credentials.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
        self.session = requests.AuthorizedSession(self.scoped_credentials)
        self.project_id = project_id
        self.location = location
        self.base_url = "https://healthcare.googleapis.com/v1"
        self.url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}"
        self.header = {"Content-Type": "application/fhir+json;charset=utf-8"}

    def create(self,
               dataset_id: str,
               fhir_store_id: str,
               resource: str,
               payload: dict
               ) -> dict:
        """Create a new resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"

        response = self.session.post(resource_path, headers=self.header, json=payload)

        return_payload = response.json()

        print(f"Created Patient resource with ID {return_payload['id']}")

        return {"response": response.status_code, "payload": return_payload}

    def update(self,
               dataset_id: str,
               fhir_store_id: str,
               resource: str,
               resource_id: str,
               payload: dict
               ) -> dict:
        """Update an existing resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"

        response = self.session.put(resource_path, headers=self.header, json=payload)

        return_payload = response.json()

        print(f"Updated {resource} resource with ID {resource_id}")

        return {"response": response.status_code, "payload": return_payload}

    def update_conditional(self,
                           dataset_id: str,
                           fhir_store_id: str,
                           resource: str,
                           condition: str,
                           payload: dict
                           ) -> dict:
        """
        If a resource is found based on the search criteria specified in the query parameters,
         updates the entire contents of that resource.
        If the search criteria identify zero matches, and the supplied resource body contains an id,
         and the FHIR store has enableUpdateCreate set, creates the resource with the client-specified ID.
        If the search criteria identify zero matches, and the supplied resource body does not contain an id,
         the resource is created with a server-assigned ID as per the create method.

        Feature only available in beta endpoint.
        See:
            https://cloud.google.com/healthcare-api/docs/reference/rest/v1beta1/projects.locations.datasets.fhirStores.fhir/conditionalUpdate

        Response code:
            200
                Updated or created successfully
            412 Precondition Failed
                If the search criteria identify more than one match

        """
        # TODO: complete response code

        base_url_beta = "https://healthcare.googleapis.com/v1beta1"
        url_beta = (f"{base_url_beta}/projects/{self.project_id}/locations/{self.location}")

        resource_path = f"{url_beta}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"
        resource_path += f"?{condition}"

        response = self.session.put(resource_path, headers=self.header, json=payload)

        return_payload = response.json()

        return {"response": response.status_code, "payload": return_payload}

    def read(self,
             dataset_id: str,
             fhir_store_id: str,
             resource: str,
             resource_id: str
             ) -> dict:
        """Read the contents of a specific resource in the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"

        response = self.session.get(resource_path, headers=self.header)

        return_payload = response.json()

        print(f"Got contents of {resource} resource with ID {resource_id}:\n")

        return {"response": response.status_code, "payload": return_payload}

    def read_conditional(self,
                         dataset_id: str,
                         fhir_store_id: str,
                         resource: str,
                         condition: str
                         ) -> dict:
        """
        If a resource is found based on the search criteria specified in the query parameters,
        read the entire contents of that resource.
        """
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}"
        resource_path += f"?{condition}"

        response = self.session.get(resource_path, headers=self.header)

        return_payload = response.json()

        print(f"Got {return_payload['total']} entries from {resource}")

        return {"response": response.status_code, "payload": return_payload}

    def delete(self,
               dataset_id: str,
               fhir_store_id: str,
               resource: str,
               resource_id: str
               ) -> dict:
        """Delete a resource from the FHIR store"""
        resource_path = f"{self.url}/datasets/{dataset_id}/fhirStores/{fhir_store_id}/fhir/{resource}/{resource_id}"

        response = self.session.delete(resource_path, headers=self.header)

        print(f"Deleted {resource} resource with ID {resource_id}.")

        return {"response": response.status_code}


class FastCRUD(HealthcareApi):
    """The  FastCRUD  class is a subclass of HealthcareApi that provides additional convenience methods for most common CRUD actions."""

    def __init__(self, project_id, location):
        super().__init__(project_id, location)

    def resource_search_lastupdated(self,
                                    dataset_id: str,
                                    fhir_store_id: str,
                                    resource: str,
                                    since: str
                                    ) -> dict:
        """Read the entries from a resource in the FHIR store that were last updated after a specific date and time"""
        parameter = f"_lastUpdated=gt{since}"
        return self.read_conditional(dataset_id, fhir_store_id, resource, parameter)

    def patient_search(self,
                       dataset_id: str,
                       fhir_store_id: str,
                       cpf: str
                       ) -> dict:
        """Read the entries from Patient resource in the FHIR store based on tax id (CPF)"""
        parameter = f"identifier=https://rnds-fhir.saude.gov.br/NamingSystem/cpf|{cpf}"
        return self.read_conditional(dataset_id, fhir_store_id, "Patient", parameter)

    def patient_update(self,
                       dataset_id: str,
                       fhir_store_id: str,
                       cpf: str,
                       payload: dict
                       ) -> dict:
        """Update the entries from Patient resource in the FHIR store based on tax id (CPF)"""
        parameter = f"identifier=https://rnds-fhir.saude.gov.br/NamingSystem/cpf|{cpf}"
        return self.update_conditional(dataset_id, fhir_store_id, "Patient", parameter, payload)
