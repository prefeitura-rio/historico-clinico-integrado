# -*- coding: utf-8 -*-
# =============================================
# TABLE MODELS
# =============================================
# - Pydantic Models Representing Datalake Tables.
# These models describe the format that every
# row sent to the Datalake must follow.
# - Also, configuration of the table name,
# dataset, etc must be provided.
# =============================================
from typing import Optional
from pydantic import BaseModel


# ===============
# SMSRio
# ===============
class SMSRioPaciente(BaseModel):
    patient_cpf: str
    source_updated_at: str
    source_id: Optional[str]
    data__nome: Optional[str]
    data__nome_mae: Optional[str]
    data__nome_pai: Optional[str]
    data__dt_nasc: Optional[str]
    data__sexo: Optional[str]
    data__racaCor: Optional[str]
    data__nacionalidade: Optional[str]
    data__obito: Optional[str]
    data__dt_obito: Optional[str]
    data__end_tp_logrado_cod: Optional[str]
    data__end_logrado: Optional[str]
    data__end_numero: Optional[str]
    data__end_comunidade: Optional[str]
    data__end_complem: Optional[str]
    data__end_bairro: Optional[str]
    data__end_cep: Optional[str]
    data__cod_mun_res: Optional[str]
    data__uf_res: Optional[str]
    data__cod_mun_nasc: Optional[str]
    data__uf_nasc: Optional[str]
    data__cod_pais_nasc: Optional[str]
    data__email: Optional[str]
    data__timestamp: Optional[str]
    data__cns_provisorio: Optional[str]
    data__telefones: Optional[str]
    payload_cnes: str

    class Config:
        dataset_id = "brutos_plataforma_smsrio"
        table_id = "paciente_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


# ===============
# Vitacare
# ===============
class VitacarePaciente(BaseModel):
    patient_cpf: str
    patient_code: str
    source_updated_at: str
    source_id: Optional[str]
    data__ap: Optional[str]
    data__id: Optional[str]
    data__cep: Optional[str]
    data__cns: Optional[str]
    data__cpf: Optional[str]
    data__dnv: Optional[str]
    data__nis: Optional[str]
    data__cnes: Optional[str]
    data__nome: Optional[str]
    data__sexo: Optional[str]
    data__email: Optional[str]
    data__obito: Optional[str]
    data__bairro: Optional[str]
    data__equipe: Optional[str]
    data__nPront: Optional[str]
    data__comodos: Optional[str]
    data__nomeMae: Optional[str]
    data__nomePai: Optional[str]
    data__racaCor: Optional[str]
    data__unidade: Optional[str]
    data__ocupacao: Optional[str]
    data__religiao: Optional[str]
    data__telefone: Optional[str]
    data__ineEquipe: Optional[str]
    data__microarea: Optional[str]
    data__logradouro: Optional[str]
    data__nomeSocial: Optional[str]
    data__destinoLixo: Optional[str]
    data__luzEletrica: Optional[str]
    data__codigoEquipe: Optional[str]
    data__dataCadastro: Optional[str]
    data__escolaridade: Optional[str]
    data__tempoMoradia: Optional[str]
    data__nacionalidade: Optional[str]
    data__rendaFamiliar: Optional[str]
    data__tipoDomicilio: Optional[str]
    data__dataNascimento: Optional[str]
    data__paisNascimento: Optional[str]
    data__tipoLogradouro: Optional[str]
    data__tratamentoAgua: Optional[str]
    data__emSituacaoDeRua: Optional[str]
    data__frequentaEscola: Optional[str]
    data__meiosTransporte: Optional[str]
    data__situacaoUsuario: Optional[str]
    data__doencasCondicoes: Optional[str]
    data__estadoNascimento: Optional[str]
    data__estadoResidencia: Optional[str]
    data__identidadeGenero: Optional[str]
    data__meiosComunicacao: Optional[str]
    data__orientacaoSexual: Optional[str]
    data__possuiFiltroAgua: Optional[str]
    data__possuiPlanoSaude: Optional[str]
    data__situacaoFamiliar: Optional[str]
    data__territorioSocial: Optional[str]
    data__abastecimentoAgua: Optional[str]
    data__animaisNoDomicilio: Optional[str]
    data__cadastroPermanente: Optional[str]
    data__familiaLocalizacao: Optional[str]
    data__emCasoDoencaProcura: Optional[str]
    data__municipioNascimento: Optional[str]
    data__municipioResidencia: Optional[str]
    data__responsavelFamiliar: Optional[str]
    data__esgotamentoSanitario: Optional[str]
    data__situacaoMoradiaPosse: Optional[str]
    data__situacaoProfissional: Optional[str]
    data__vulnerabilidadeSocial: Optional[str]
    data__familiaBeneficiariaCfc: Optional[str]
    data__dataAtualizacaoCadastro: Optional[str]
    data__participaGrupoComunitario: Optional[str]
    data__relacaoResponsavelFamiliar: Optional[str]
    data__membroComunidadeTradicional: Optional[str]
    data__dataAtualizacaoVinculoEquipe: Optional[str]
    data__familiaBeneficiariaAuxilioBrasil: Optional[str]
    data__criancaMatriculadaCrechePreEscola: Optional[str]
    payload_cnes: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "paciente_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


class VitacareAtendimento(BaseModel):
    patient_cpf: str
    patient_code: str
    source_updated_at: str
    source_id: str
    data__unidade_ap: str
    data__unidade_cnes: str
    data__profissional__cns: Optional[str]
    data__profissional__cpf: Optional[str]
    data__profissional__nome: Optional[str]
    data__profissional__cbo: Optional[str]
    data__profissional__cbo_descricao: Optional[str]
    data__profissional__equipe__nome: Optional[str]
    data__profissional__equipe__cod_equipe: Optional[str]
    data__profissional__equipe__cod_ine: Optional[str]
    data__datahora_inicio_atendimento: str
    data__datahora_fim_atendimento: str
    data__datahora_marcacao_atendimento: Optional[str]
    data__tipo_consulta: str
    data__eh_coleta: str
    data__soap_subjetivo_motivo: Optional[str]
    data__soap_plano_procedimentos_clinicos: Optional[str]
    data__soap_plano_observacoes: Optional[str]
    data__soap_avaliacao_observacoes: Optional[str]
    data__soap_objetivo_descricao: Optional[str]
    data__notas_observacoes: Optional[str]
    data__condicoes: str
    data__prescricoes: str
    data__exames_solicitados: str
    data__vacinas: str
    data__alergias_anamnese: str
    data__indicadores: str
    data__encaminhamentos: str
    payload_cnes: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "atendimento_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


class VitacareProcedimentosClinicos(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    procedimentoClinico: str
    observacao: Optional[str]

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "procedimentos_clinicos_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


class VitacareCondicao(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    cod_cid10: str
    cod_ciap2: Optional[str]
    estado: str
    data_diagnostico: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "condicoes_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


class VitacareAlergia(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    descricao: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "alergia_anamnese_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"
        biglake_table = True
        dataset_is_public = False


class VitacareEncaminhamento(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    descricao: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "encaminhamento_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"


class VitacarePrescricao(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    nome_medicamento: str
    cod_medicamento: str
    quantidade: str
    uso_continuado: bool

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "prescricao_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"


class VitacareExameSolicitado(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    nome_exame: str
    cod_exame: str
    quantidade: str
    material: str
    url_resultado: Optional[str]
    data_solicitacao: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "exames_solicitados_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"


class VitacareVacina(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    nome_vacina: str
    cod_vacina: str
    dose: str
    lote: str
    datahora_aplicacao: str
    datahora_registro: str
    diff: str
    calendario_vacinal_atualizado: bool
    dose_vtc: str
    tipo_registro: str
    estrategia_imunizacao: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "vacinas_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"


class VitacareIndicador(BaseModel):
    patient_cpf: str
    atendimento_id: str
    source_updated_at: str
    nome: str
    valor: str

    class Config:
        dataset_id = "brutos_prontuario_vitacare"
        table_id = "indicadores_eventos"
        partition_by_date = True
        partition_column = "source_updated_at"