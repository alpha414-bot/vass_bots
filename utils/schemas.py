from pydantic import BaseModel
from typing import Optional, Annotated
from fastapi import Query


class Anagrafica(BaseModel):
    cf: Annotated[str, Query(min_length=2)]  # Codice Fiscale (Tax Code)
    nascitaGiorno: Annotated[str, Query(min_length=1)]  # Birth Day (Optional)
    nascitaMese: Annotated[str, Query(min_length=1)]  # Birth Month (Optional)
    nascitaAnno: int | str  # Birth Year (Optional)
    patenteAnno: int | str  # Driving License Year (Optional)
    residenzaProvincia: Annotated[
        str, Query(min_length=1)
    ]  # Residence Province (Optional)
    residenzaComune: Annotated[str, Query(min_length=2)]  # Residence City (Optional)
    residenzaIndirizzoVia: Annotated[
        str, Query(min_length=1)
    ]  # Residence Street Name (Optional)
    residenzaIndirizzo: Annotated[
        str, Query(min_length=1)
    ]  # Residence Street (Optional)
    residenzaCivico: Annotated[str, Query(min_length=1)]  # Residence Number (Optional)


class Veicolo(BaseModel):
    targa: Annotated[str, Query(min_length=2)]  # License Plate (Optional)
    acquistoGiorno: Annotated[str, Query(min_length=1)]  # Purchase Day (Optional)
    acquistoMese: Annotated[str, Query(min_length=1)]  # Purchase Month (Optional)
    acquistoAnno: int | str  # Purchase Year (Optional)
    allestimento: Annotated[str, Query(min_length=2)]
    immatricolazioneGiorno: Annotated[
        str, Query(min_length=1)
    ]  # Registration Day (Optional)
    immatricolazioneMese: Annotated[
        str, Query(min_length=1)
    ]  # Registration Month (Optional)
    immatricolazioneAnno: int | str  # Registration Year (Optional)
    dataDecorrenza: Optional[Annotated[str, Query(min_length=2)]] = (
        None  # Coverage Start Date (Optional)
    )


class RequestData(BaseModel):
    anag: Anagrafica  # Personal Information
    veicolo: Veicolo  # Vehicle Information


class RawRequestData(BaseModel):
    request_id: Optional[str | int] = None
    request_refresh: Optional[bool] = None
    proxy: Optional[str] = None
    data: Optional[RequestData] = None
