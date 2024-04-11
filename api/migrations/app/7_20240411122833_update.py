from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE INDEX "idx_raw__patien_patient_ade974" ON "raw__patientcondition" ("patient_cpf");
        CREATE INDEX "idx_raw__patien_patient_7c92f7" ON "raw__patientcondition" ("patient_code");
        CREATE INDEX "idx_raw__patien_patient_fcf0c1" ON "raw__patientrecord" ("patient_cpf");
        CREATE INDEX "idx_raw__patien_patient_564fbe" ON "raw__patientrecord" ("patient_code");
        CREATE INDEX "idx_std__patien_patient_31db77" ON "std__patientcondition" ("patient_cpf");
        CREATE INDEX "idx_std__patien_patient_4c877e" ON "std__patientcondition" ("patient_code");
        CREATE INDEX "idx_std__patien_patient_061ca6" ON "std__patientrecord" ("patient_cpf");
        CREATE INDEX "idx_std__patien_patient_7d233d" ON "std__patientrecord" ("patient_code");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_std__patien_patient_4c877e";
        DROP INDEX "idx_std__patien_patient_31db77";
        DROP INDEX "idx_std__patien_patient_7d233d";
        DROP INDEX "idx_std__patien_patient_061ca6";
        DROP INDEX "idx_raw__patien_patient_7c92f7";
        DROP INDEX "idx_raw__patien_patient_ade974";
        DROP INDEX "idx_raw__patien_patient_564fbe";
        DROP INDEX "idx_raw__patien_patient_fcf0c1";"""
