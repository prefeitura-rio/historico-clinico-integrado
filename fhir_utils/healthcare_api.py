from googleapiclient import discovery
import json

class HealthcareApi:
    def __init__(self, project_id, location, dataset_id, fhir_store_id):
        self.api_version = "v1"
        self.service_name = "healthcare"
        self.header = "application/fhir+json;charset=utf-8"
        self.fhir_store_parent = f"projects/{project_id}/locations/{location}/datasets/{dataset_id}"
        self.fhir_store_name = f"{self.fhir_store_parent}/fhirStores/{fhir_store_id}"
        self.client = discovery.build(self.service_name, self.api_version)


    def create(self, resource: str, body: dict):
        request = self.client.projects().locations().datasets().fhirStores().fhir().create(parent = self.fhir_store_name,
                                                                                           type = resource,
                                                                                           body = body)
        request.headers["content-type"] = self.header

        response = request.execute()
        print(f"Created Patient resource with ID {response['id']}")

        return response


    def update(self, resource: str, resource_id: str, body: dict):
        fhir_resource_path = f"{self.fhir_store_name}/fhir/{resource}/{resource_id}"

        request = self.client.projects().locations().datasets().fhirStores().fhir().update(name = fhir_resource_path,
                                                                                           body = body)

        request.headers["content-type"] = self.header
        
        response = request.execute()
        print(f"Updated {resource} resource with ID {resource_id}:\n {json.dumps(response, indent=2)}")

        return response

    
    def read(self, resource: str, resource_id: str):
        fhir_resource_path = f"{self.fhir_store_name}/fhir/{resource}/{resource_id}"

        request = self.client.projects().locations().datasets().fhirStores().fhir().read(name = fhir_resource_path)

        response = request.execute()
        print(f"Got contents of {resource} resource with ID {resource_id}:\n", json.dumps(response, indent=2),)

        return response

    
    def delete(self, resource: str, resource_id: str):
        fhir_resource_path = f"{self.fhir_store_name}/fhir/{resource}/{resource_id}"

        request = self.client.projects().locations().datasets().fhirStores().fhir().delete(name = fhir_resource_path)

        response = request.execute()
        print(f"Deleted {resource} resource with ID {resource_id}.")

        return response
