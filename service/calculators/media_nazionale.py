from service.converts_paese_eurostat import converts_paese_eurostat


def get_national_average(paese: str, banda: str = "KWH2500-4999") -> dict:
    """Restituisce il prezzo medio nazionale per paese e fascia consumo."""
    dato = converts_paese_eurostat(paese, banda)
    if "errore" in dato:
        return {"errore": dato["errore"]}
    return dato
    
