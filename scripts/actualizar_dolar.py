#!/usr/bin/env python3
"""Actualiza data/tipo_cambio.json con el dólar en pesos chilenos (mindicador.cl, y si falla open.er-api.com).
Si ninguna fuente responde, deja el valor anterior: el sitio muestra la fecha del dato."""
import datetime as dt
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "tipo_cambio.json"


def get(url):
    r = subprocess.run(["curl", "-sL", "--max-time", "20", url], capture_output=True, text=True)
    return json.loads(r.stdout)


def main():
    try:
        d = get("https://mindicador.cl/api/dolar")["serie"][0]
        dato = {"clp_por_usd": round(d["valor"], 2), "fecha": d["fecha"][:10], "fuente": "Dólar observado (mindicador.cl)"}
    except Exception:
        try:
            d = get("https://open.er-api.com/v6/latest/USD")
            fecha = dt.datetime.strptime(d["time_last_update_utc"], "%a, %d %b %Y %H:%M:%S %z").date().isoformat()
            dato = {"clp_por_usd": round(d["rates"]["CLP"], 2), "fecha": fecha, "fuente": "open.er-api.com"}
        except Exception as ex:
            print("Sin dato nuevo de dólar, se mantiene el anterior:", ex)
            return
    OUT.write_text(json.dumps(dato, ensure_ascii=False, indent=2) + "\n")
    print("Dólar:", dato)


if __name__ == "__main__":
    main()
