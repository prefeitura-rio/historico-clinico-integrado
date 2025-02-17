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
from datetime import datetime
from pydantic import BaseModel


# ===============
# SMSRio
# ===============
class SMSRioPaciente(BaseModel):
    patient_cpf: Optional[str]
    source_id: str
    source_updated_at: str
    datalake_loaded_at: str = datetime.now().isoformat()

    # Campos adicionais
    data__id: Optional[str]
    data__mpi: Optional[str]
    data__cpf: Optional[str]
    data__nome: Optional[str]
    data__nome_social: Optional[str]
    data__nome_mae: Optional[str]
    data__nome_pai: Optional[str]
    data__dt_nasc: Optional[str]
    data__sexo: Optional[str]
    data__racaCor: Optional[str]
    data__codigoRacaCor: Optional[str]
    data__tp_sangue: Optional[str]
    data__end_tp_logrado_nm: Optional[str]
    data__end_tp_logrado_cod: Optional[str]
    data__end_logrado: Optional[str]
    data__end_numero: Optional[str]
    data__end_comunidade: Optional[str]
    data__end_complem: Optional[str]
    data__end_bairro: Optional[str]
    data__end_cod_bairro: Optional[str]
    data__end_cep: Optional[str]
    data__cod_mun_nasc: Optional[str]
    data__munic_nasc: Optional[str]
    data__uf_nasc: Optional[str]
    data__cod_pais_nasc: Optional[str]
    data__pais_nasc: Optional[str]
    data__nacionalidade: Optional[str]
    data__cod_mun_res: Optional[str]
    data__munic_res: Optional[str]
    data__uf_res: Optional[str]
    data__tp_telefone: Optional[str]
    data__tel_resid: Optional[str]
    data__tel_cel: Optional[str]
    data__tp_email: Optional[str]
    data__email: Optional[str]
    data__ap: Optional[str]
    data__cnes_res: Optional[str]
    data__nome_ub_res: Optional[str]
    data__cod_area: Optional[str]
    data__cod_microa: Optional[str]
    data__lat: Optional[str]
    data__lng: Optional[str]
    data__dnv: Optional[str]
    data__nis: Optional[str]
    data__rg: Optional[str]
    data__rg_dt: Optional[str]
    data__rg_emis: Optional[str]
    data__rg_uf: Optional[str]
    data__cnh: Optional[str]
    data__cnh_dt: Optional[str]
    data__cnh_uf: Optional[str]
    data__doc_cert_tp: Optional[str]
    data__doc_cert_cart: Optional[str]
    data__doc_cert_livro: Optional[str]
    data__doc_cert_folha: Optional[str]
    data__doc_cert_termo: Optional[str]
    data__doc_cert_dt: Optional[str]
    data__doc_cert_uf: Optional[str]
    data__doc_cert_cod_mun: Optional[str]
    data__doc_cert_matricula: Optional[str]
    data__tit_eleit: Optional[str]
    data__tit_eleit_zona: Optional[str]
    data__tit_eleit_sec: Optional[str]
    data__ctps_numero: Optional[str]
    data__ctps_serie: Optional[str]
    data__ctps_dt: Optional[str]
    data__pass: Optional[str]
    data__pass_pais: Optional[str]
    data__pass_dt_val: Optional[str]
    data__pass_dt_exp: Optional[str]
    data__dt_cadastro: Optional[str]
    data__obito: Optional[str]
    data__dt_obito: Optional[str]
    data__counter: Optional[str]
    data__cpf_valido: Optional[str]
    data__origem: Optional[str]
    data__cns_tp: Optional[str]
    data__cns_dt_ativa: Optional[str]
    data__ativo: Optional[str]
    data__timestamp: Optional[str]
    data__cns_provisorio: Optional[str]
    data__telefones: Optional[str]

    class Config:
        dataset_id = "brutos_plataforma_smsrio"
        table_id = "_paciente_eventos"
        biglake_table = False
        date_partition_column = "datalake_loaded_at"


# ===============
# Vitacare
# ===============
class VitacarePaciente(BaseModel):
    patient_cpf: str
    patient_code: str
    source_updated_at: str
    source_id: Optional[str]
    datalake_loaded_at: str = datetime.now().isoformat()
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
        table_id = "_paciente_eventos"
        biglake_table = False
        date_partition_column = "datalake_loaded_at"


class VitacareAtendimento(BaseModel):
    patient_cpf: str
    patient_code: str
    source_updated_at: str
    source_id: str
    datalake_loaded_at: str = datetime.now().isoformat()
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
        table_id = "_atendimento_eventos"
        biglake_table = False
        date_partition_column = "datalake_loaded_at"
