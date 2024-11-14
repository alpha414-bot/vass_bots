from pydantic import BaseModel
from typing import Optional, Annotated
from fastapi import Query


class Anagrafica(BaseModel):
    cf: str = "BNDCML75M61F839P"  # Codice Fiscale (Tax Code)
    nascitaGiorno: str = "21"  # Birth Day (Optional)
    nascitaMese: str = "08"  # Birth Month (Optional)
    nascitaAnno: int | str = 1975  # Birth Year (Optional)
    patenteAnno: int | str = "1993"  # Driving License Year (Optional)
    residenzaProvincia: str = "NA"  # Residence Province (Optional)
    residenzaComune: str = "SANT'ANASTASIA"  # Residence City (Optional)
    residenzaIndirizzoVia: str = "VIA"  # Residence Street Name (Optional)
    residenzaIndirizzo: str = "SOMMA"  # Residence Street (Optional)
    residenzaCivico: str = "57"  # Residence Number (Optional)


class Veicolo(BaseModel):
    targa: str = "CL962LD"  # License Plate (Optional)
    acquistoGiorno: str = "04"  # Purchase Day (Optional)
    acquistoMese: str = "10"  # Purchase Month (Optional)
    acquistoAnno: int | str = 2019  # Purchase Year (Optional)
    allestimento: str = "Panda 1.2 Dynamic"
    immatricolazioneGiorno: str = "30"  # Registration Day (Optional)
    immatricolazioneMese: str = "06"  # Registration Month (Optional)
    immatricolazioneAnno: int | str = 20055  # Registration Year (Optional)
    dataDecorrenza: Optional[Annotated[str, Query(min_length=2)]] = (
        None  # Coverage Start Date (Optional)
    )


class DatiPreventivo(BaseModel):
    idAccordo: int = 72  # Agreement ID
    idFascia: int = 1  # Rate Class ID


class SubRequestData(BaseModel):
    anag: Anagrafica  # Personal Information
    veicolo: Veicolo  # Vehicle Information
    datiPreventivo: DatiPreventivo


class RawRequestData(BaseModel):
    request_id: Optional[str | int] = None
    request_refresh: Optional[bool] = None
    proxy: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    data: Optional[SubRequestData] = None


class RequestData(BaseModel):
    request_id: Optional[str | int] = None
    request_refresh: Optional[bool] = None
    proxy: Optional[str] = None
    botId: int
    remoteHost: str
    idPrev: int
