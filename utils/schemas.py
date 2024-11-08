from pydantic import BaseModel
from typing import List, Optional


class DatiPreventivo(BaseModel):
    idRicerca: int  # Search ID
    idAnag: int  # Personal ID
    idveicolo: int  # Vehicle ID
    idAnagPIVA: Optional[int] = None  # Business ID (Optional)
    idPreventivo: int  # Quote ID
    idAccordo: int  # Agreement ID
    idFascia: int  # Rate Class ID
    provenienzaIdValore: int  # Value of Origin ID
    idScelta: Optional[int] = None  # Choice ID (Optional)


class Anagrafica(BaseModel):
    cf: str  # Codice Fiscale (Tax Code)
    cognome: str  # Last Name
    nome: str  # First Name
    sesso: str  # Gender (M/F)
    nascitaGiorno: Optional[str] = None  # Birth Day (Optional)
    nascitaMese: Optional[str] = None  # Birth Month (Optional)
    nascitaAnno: Optional[int] = None  # Birth Year (Optional)
    nascitaComune: Optional[str] = None  # Birth City (Optional)
    nascitaCodiceComune: Optional[str] = None  # Birth City Code (Optional)
    nascitaCodiceCatastale: Optional[str] = None  # Birth Cadastral Code (Optional)
    nascitaProvincia: Optional[str] = None  # Birth Province (Optional)
    nascitaProvinciaEstesa: Optional[str] = None  # Full Province Name (Optional)
    nascitaNazione: Optional[str] = None  # Birth Country (Optional)
    patenteAnno: Optional[str] = None  # Driving License Year (Optional)
    residenzaIndirizzoVia: Optional[str] = None  # Residence Street Name (Optional)
    residenzaIndirizzo: Optional[str] = None  # Residence Street (Optional)
    residenzaCivico: Optional[str] = None  # Residence Number (Optional)
    residenzaCAP: Optional[str] = None  # Postal Code (Optional)
    residenzaComune: Optional[str] = None  # Residence City (Optional)
    residenzaProvincia: Optional[str] = None  # Residence Province (Optional)
    residenzaCodiceComune: Optional[str] = None  # Residence City Code (Optional)
    residenzaCodiceCatastaleComune: Optional[str] = (
        None  # Residence Cadastral Code (Optional)
    )
    email: Optional[str] = None  # Email Address (Optional)
    cellulare: Optional[str] = None  # Mobile Number (Optional)
    tipoGuida: Optional[str] = None  # Driving Experience Type (Optional)
    eta: Optional[int] = None  # Age (Optional)


class Attestato(BaseModel):
    anno: int  # Year
    principale: str  # Main (claims type)
    principaleCose: str  # Main - Goods
    principaleMisti: str  # Main - Mixed
    principalePersone: str  # Main - People
    paritaria: str  # Parity (claims type)
    paritariaCose: str  # Parity - Goods
    paritariaMisti: str  # Parity - Mixed
    paritariaPersone: str  # Parity - People


class AttestatoDetails(BaseModel):
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


class Veicolo(BaseModel):
    targa: Optional[str] = None  # License Plate (Optional)
    marca: Optional[str] = None  # Brand (Optional)
    modello: Optional[str] = None  # Model (Optional)
    allestimento: Optional[str] = None  # Configuration (Optional)
    immatricolazioneGiorno: Optional[str] = None  # Registration Day (Optional)
    immatricolazioneMese: Optional[str] = None  # Registration Month (Optional)
    immatricolazioneAnno: Optional[int] = None  # Registration Year (Optional)
    acquistoGiorno: Optional[str] = None  # Purchase Day (Optional)
    acquistoMese: Optional[str] = None  # Purchase Month (Optional)
    acquistoAnno: Optional[int] = None  # Purchase Year (Optional)
    alimentazione: Optional[str] = None  # Fuel Type (Optional)
    tipoVeicolo: Optional[str] = None  # Vehicle Type (Optional)
    formaTariffaria: Optional[str] = None  # Rate Type (Optional)
    cilindrata: Optional[str] = None  # Engine Capacity (Optional)
    cilindrataAbb: Optional[str] = None  # Engine Capacity (Abbreviated) (Optional)
    dataDecorrenza: Optional[str] = None  # Coverage Start Date (Optional)
    dataFineCopertura: Optional[str] = None  # Coverage End Date (Optional)
    dataMora: Optional[str] = None  # Penalty Date (Optional)
    dataScadenzaAttestato: Optional[str] = None  # Attestation Expiry Date (Optional)
    classeMerito: Optional[str] = None  # Bonus-Malus Class (Optional)
    provenienzaCU: Optional[str] = None  # Origin CU (Optional)
    anniAssicurazione: Optional[str] = None  # Insurance Years (Optional)
    anniZeroSinistri: Optional[int] = None  # Zero Claims Years (Optional)
    assicurazioneProvenienza: Optional[str] = None  # Insurance Provider (Optional)
    kw: Optional[int] = None  # Kilowatt (Power) (Optional)
    cavalliFiscali: Optional[int] = None  # Fiscal Horsepower (Optional)
    etaVeicoloMesi: Optional[int] = None  # Vehicle Age in Months (Optional)
    uso: Optional[str] = None  # Usage (Optional)
    massaQuintali: Optional[str] = None  # Weight in Quintals (Optional)
    massaRimorchiabile: Optional[str] = None  # Towing Capacity (Optional)
    kmPercorsi: Optional[int] = None  # Mileage (Optional)
    attestato: Optional[List[Attestato]] = (
        None  # Claims Attestation per Year (Optional)
    )
    attestatoDetails: Optional[AttestatoDetails] = (
        None  # Detailed Claims Information (Optional)
    )


class PartitaIVA(BaseModel):
    pass  # Empty, as no data is provided


class Portante(BaseModel):
    pass  # Empty, as no data is provided


class Utenti(BaseModel):
    preventiviCellulare: Optional[str] = None  # Mobile for Quote (Optional)
    preventiviEmail: Optional[str] = None  # Email for Quote (Optional)
    nomeUtente: Optional[str] = None  # Username (Optional)
    passw: Optional[str] = None  # Password (Optional)


class Details(BaseModel):
    pass  # Empty, as no data is provided


class RequestData(BaseModel):
    datiPreventivo: DatiPreventivo  # Quote Data
    anag: Anagrafica  # Personal Information
    veicolo: Veicolo  # Vehicle Information
    partitaIVA: PartitaIVA  # Business ID (Optional)
    portante: Portante  # Empty, as no data is provided
    utenti: Utenti  # User Information
    details: Details  # Empty, as no data is provided


class RawRequestData(BaseModel):
    status: Optional[str] = None
    message: Optional[str] = None
    data: RequestData
