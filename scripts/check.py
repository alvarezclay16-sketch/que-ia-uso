#!/usr/bin/env python3
"""Revisa datos y sitio generado antes de publicar. Sale con código 1 si hay errores.

Uso: python3 scripts/check.py            (datos + enlaces internos)
     python3 scripts/check.py --online   (además prueba que los enlaces externos respondan)
"""
import datetime as dt
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs"
errors, warns = [], []

cfg = json.loads((DATA / "config.json").read_text())
cats = json.loads((DATA / "categorias.json").read_text())
tools = json.loads((DATA / "herramientas.json").read_text())
news = json.loads((DATA / "novedades.json").read_text())
spons = json.loads((DATA / "patrocinios.json").read_text())
cat_ids = {c["id"] for c in cats}
today = dt.date.today()

REQ = ["nombre", "url", "empresa", "plan_gratis", "mejor_para", "veredicto", "espanol", "fuente", "verificado"]
for cid, lst in tools.items():
    if cid not in cat_ids:
        errors.append(f"herramientas.json: categoría desconocida {cid}")
    if len(lst) < 3:
        warns.append(f"{cid}: solo {len(lst)} herramientas")
    names = set()
    for t in lst:
        for k in REQ:
            if k not in t or t[k] in ("", None) and k not in ("plan_gratis", "espanol"):
                errors.append(f"{cid}/{t.get('nombre')}: falta {k}")
        if t.get("nombre") in names:
            errors.append(f"{cid}: duplicada {t['nombre']}")
        names.add(t.get("nombre"))
        for k in ("url", "fuente"):
            if t.get(k) and not str(t[k]).startswith("https://"):
                errors.append(f"{cid}/{t['nombre']}: {k} no es https")
        if t.get("verificado"):
            age = (today - dt.date.fromisoformat(t["verificado"])).days
            if age > 90:
                warns.append(f"{cid}/{t['nombre']}: verificado hace {age} días")
for c in cats:
    if c["id"] not in tools:
        errors.append(f"categoría sin herramientas: {c['id']}")

for n in news:
    for k in ("fecha", "titulo", "resumen", "fuente"):
        if not n.get(k):
            errors.append(f"novedad sin {k}: {n.get('titulo')}")
    if n.get("fecha") and dt.date.fromisoformat(n["fecha"]) > today:
        errors.append(f"novedad con fecha futura: {n['titulo']}")
    if n.get("categoria") and n["categoria"] not in cat_ids:
        errors.append(f"novedad con categoría desconocida: {n['titulo']}")
for k in ("pago_destacado_categoria", "pago_destacado_portada"):
    if cfg.get(k) and not cfg[k].startswith("https://"):
        errors.append(f"config.json: {k} debe ser un link https")
for s in spons:
    if s.get("categoria") not in cat_ids | {"portada", "novedades"}:
        errors.append(f"patrocinio con ubicación desconocida: {s}")

# Sitio generado
if not OUT.exists():
    errors.append("no existe docs/: corre scripts/build.py")
else:
    bp = cfg["base_path"].rstrip("/")
    for c in cats:
        if not (OUT / "para" / c["id"] / "index.html").exists():
            errors.append(f"falta página de {c['id']}")
    for f in ("index.html", "404.html", "llms.txt", "llms-full.txt", "sitemap.xml", "robots.txt", "feed.xml", "assets/style.css"):
        if not (OUT / f).exists():
            errors.append(f"falta {f}")
    external = set()
    for page in OUT.rglob("*.html"):
        txt = page.read_text()
        if re.search(r"\{[a-z_]+\}", re.sub(r"<script.*?</script>", "", txt, flags=re.S)):
            errors.append(f"{page.relative_to(OUT)}: quedó un marcador sin reemplazar")
        for href in re.findall(r'href="([^"]+)"', txt):
            if href.startswith(bp + "/"):
                rel = href[len(bp):].split("#")[0]
                target = OUT / rel.lstrip("/")
                if rel.endswith("/"):
                    target = target / "index.html"
                if not target.exists():
                    errors.append(f"{page.relative_to(OUT)}: enlace roto {href}")
            elif href.startswith("http"):
                external.add(href.replace("&amp;", "&"))
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', txt, flags=re.S):
            try:
                json.loads(m)
            except Exception as ex:
                errors.append(f"{page.relative_to(OUT)}: JSON-LD inválido {ex}")

    if "--online" in sys.argv:
        skip = ("https://github.com/" + cfg["repo"], cfg["base_url"])

        def probe(u):
            import subprocess
            r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-A",
                                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/141 Safari/537.36",
                                "-w", "%{http_code}", u], capture_output=True, text=True)
            code = r.stdout.strip()
            return u, int(code) if code.isdigit() and code != "000" else "sin respuesta"

        todo = [u for u in external if not u.startswith(skip) and "zgo.at" not in u]
        with ThreadPoolExecutor(12) as ex:
            for u, st in ex.map(probe, todo):
                if st == 404 or st == 410 or isinstance(st, str):
                    warns.append(f"enlace externo con problema ({st}): {u}")

for w in warns:
    print("AVISO ", w)
for er in errors:
    print("ERROR ", er)
print(f"{len(errors)} errores, {len(warns)} avisos")
sys.exit(1 if errors else 0)
