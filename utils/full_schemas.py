from pydantic import BaseModel
from typing import Optional, Annotated
from fastapi import Query


class _DatiPreventivo(BaseModel):
    idRicerca: int  # Search ID
    idAnag: int  # Personal ID
    idveicolo: int  # Vehicle ID
    idAnagPIVA: Optional[int] = None  # Business ID (Optional)
    idPreventivo: int  # Quote ID
    idAccordo: int  # Agreement ID
    idFascia: int  # Rate Class ID
    provenienzaIdValore: int  # Value of Origin ID
    idScelta: Optional[int] = None  # Choice ID (Optional)


class _Anagrafica(BaseModel):
    cf: str  # Codice Fiscale (Tax Code)
    nascitaGiorno: str  # Birth Day (Optional)
    nascitaMese: str  # Birth Month (Optional)
    nascitaAnno: int  # Birth Year (Optional)
    patenteAnno: str  # Driving License Year (Optional)
    residenzaProvincia: str  # Residence Province (Optional)
    residenzaComune: str  # Residence City (Optional)
    residenzaIndirizzoVia: str  # Residence Street Name (Optional)
    residenzaIndirizzo: str  # Residence Street (Optional)
    residenzaCivico: str  # Residence Number (Optional)
    # cognome: str  # Last Name
    # nome: str  # First Name
    # sesso: str  # Gender (M/F)
    # nascitaComune: Optional[str] = None  # Birth City (Optional)
    # nascitaCodiceComune: Optional[str] = None  # Birth City Code (Optional)
    # nascitaCodiceCatastale: Optional[str] = None  # Birth Cadastral Code (Optional)
    # nascitaProvincia: Optional[str] = None  # Birth Province (Optional)
    # nascitaProvinciaEstesa: Optional[str] = None  # Full Province Name (Optional)
    # nascitaNazione: Optional[str] = None  # Birth Country (Optional)
    # residenzaCAP: Optional[str] = None  # Postal Code (Optional)
    # residenzaCodiceComune: Optional[str] = None  # Residence City Code (Optional)
    # residenzaCodiceCatastaleComune: Optional[str] = (
    #     None  # Residence Cadastral Code (Optional)
    # )
    # email: Optional[str] = None  # Email Address (Optional)
    # cellulare: Optional[str] = None  # Mobile Number (Optional)
    # tipoGuida: Optional[str] = None  # Driving Experience Type (Optional)
    # eta: Optional[int] = None  # Age (Optional)


class _Attestato(BaseModel):
    anno: int  # Year
    principale: str  # Main (claims type)
    principaleCose: str  # Main - Goods
    principaleMisti: str  # Main - Mixed
    principalePersone: str  # Main - People
    paritaria: str  # Parity (claims type)
    paritariaCose: str  # Parity - Goods
    paritariaMisti: str  # Parity - Mixed
    paritariaPersone: str  # Parity - People


class _AttestatoDetails(BaseModel):
    SinistriUltimi2Anni: Optional[int] = None  # Claims in Last 2 Years (Optional)
    totPrimoAnnoVis: Optional[int] = None  # Total First Year Claims (Optional)
    totAnniVis: Optional[int] = None  # Total Years of Claims (Optional)
    totSinPriVis: Optional[int] = None  # Total Primary Claims (Optional)
    totSinParVis: Optional[int] = None  # Total Parity Claims (Optional)
    totCardIAttVis: Optional[int] = None  # Total Active Card Claims (Optional)
    totCardIPasVis: Optional[int] = None  # Total Inactive Card Claims (Optional)
    totPrimoAnnoVisCont: Optional[int] = None  # Contingent First Year Claims (Optional)
    totAnniVisCont: Optional[int] = None  # Contingent Years of Claims (Optional)
    totSinPriVisCont: Optional[int] = None  # Contingent Primary Claims (Optional)
    totSinParVisCont: Optional[int] = None  # Contingent Parity Claims (Optional)
    totCardIAttVisCont: Optional[int] = None  # Contingent Active Card Claims (Optional)
    totCardIPasVisCont: Optional[int] = (
        None  # Contingent Inactive Card Claims (Optional)
    )


class _Veicolo(BaseModel):
    targa: Annotated[str, Query(min_length=2)]  # License Plate (Optional)
    acquistoGiorno: Annotated[str, Query(min_length=2)]  # Purchase Day (Optional)
    acquistoMese: Annotated[str, Query(min_length=2)]  # Purchase Month (Optional)
    acquistoAnno: Annotated[int, Query(min_length=4)]  # Purchase Year (Optional)
    allestimento: Annotated[str, Query(min_length=2)]  # Configuration (Optional)
    immatricolazioneGiorno: str  # Registration Day (Optional)
    immatricolazioneMese: str  # Registration Month (Optional)
    immatricolazioneAnno:   # Registration Year (Optional)
    dataDecorrenza: Optional[str] = None  # Coverage Start Date (Optional)

    # marca: Optional[str] = None  # Brand (Optional)
    # modello: Optional[str] = None  # Model (Optional)
    # alimentazione: Optional[str] = None  # Fuel Type (Optional)
    # tipoVeicolo: Optional[str] = None  # Vehicle Type (Optional)
    # formaTariffaria: Optional[str] = None  # Rate Type (Optional)
    # cilindrata: Optional[str] = None  # Engine Capacity (Optional)
    # cilindrataAbb: Optional[str] = None  # Engine Capacity (Abbreviated) (Optional)
    # dataFineCopertura: Optional[str] = None  # Coverage End Date (Optional)
    # dataMora: Optional[str] = None  # Penalty Date (Optional)
    # dataScadenzaAttestato: Optional[str] = None  # Attestation Expiry Date (Optional)
    # classeMerito: Optional[str] = None  # Bonus-Malus Class (Optional)
    # provenienzaCU: Optional[str] = None  # Origin CU (Optional)
    # anniAssicurazione: Optional[str] = None  # Insurance Years (Optional)
    # anniZeroSinistri: Optional[int] = None  # Zero Claims Years (Optional)
    # assicurazioneProvenienza: Optional[str] = None  # Insurance Provider (Optional)
    # kw: Optional[int] = None  # Kilowatt (Power) (Optional)
    # cavalliFiscali: Optional[int] = None  # Fiscal Horsepower (Optional)
    # etaVeicoloMesi: Optional[int] = None  # Vehicle Age in Months (Optional)
    # uso: Optional[str] = None  # Usage (Optional)
    # massaQuintali: Optional[str] = None  # Weight in Quintals (Optional)
    # massaRimorchiabile: Optional[str] = None  # Towing Capacity (Optional)
    # kmPercorsi: Optional[int] = None  # Mileage (Optional)
    # attestato: Optional[List[Attestato]] = (
    #     None  # Claims Attestation per Year (Optional)
    # )
    # attestatoDetails: Optional[AttestatoDetails] = (
    #     None  # Detailed Claims Information (Optional)
    # )


class _PartitaIVA(BaseModel):
    pass  # Empty, as no data is provided


class _Portante(BaseModel):
    pass  # Empty, as no data is provided


class _Utenti(BaseModel):
    preventiviCellulare: Optional[str] = None  # Mobile for Quote (Optional)
    preventiviEmail: Optional[str] = None  # Email for Quote (Optional)
    nomeUtente: Optional[str] = None  # Username (Optional)
    passw: Optional[str] = None  # Password (Optional)


class _Details(BaseModel):
    pass  # Empty, as no data is provided


class _RequestData(BaseModel):
    anag: _Anagrafica  # Personal Information
    veicolo: _Veicolo  # Vehicle Information


class _RawRequestData(BaseModel):
    request_id: Optional[str] = None
    request_refresh: Optional[bool] = None
    proxy: Optional[str] = None
    data: _RequestData
    # status: Optional[str] = None
    # message: Optional[str] = None
