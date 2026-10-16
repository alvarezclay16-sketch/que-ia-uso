#!/usr/bin/env python3
"""Genera el sitio estático de Qué IA Uso en docs/ a partir de data/*.json.

Uso: python3 scripts/build.py
Solo biblioteca estándar, para que el bot CEO lo pueda correr siempre.
"""
import datetime as dt
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs"
ASSETS = ROOT / "assets"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def load(name, default=None):
    p = DATA / name
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


CFG = load("config.json")
CATS = load("categorias.json")
TOOLS = load("herramientas.json", {})
NEWS = sorted(load("novedades.json", []), key=lambda n: n["fecha"], reverse=True)
SPONS = load("patrocinios.json", [])
KEYS = load("busqueda.json", {})
TODAY = dt.date.today()
MES = f"{MESES[TODAY.month - 1]} de {TODAY.year}"
MES_CORTO = f"{MESES[TODAY.month - 1]} {TODAY.year}"
BP = CFG["base_path"].rstrip("/")
BU = CFG["base_url"].rstrip("/")

e = html.escape


def fecha_larga(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def recortar(s, n=155):
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0] + "…"


def link(path):
    return f"{BP}{path}"


def ext(url, text, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{e(url)}"{c} target="_blank" rel="noopener">{text}</a>'


def sponsors_for(where):
    out = []
    for s in SPONS:
        if s.get("categoria") != where:
            continue
        if s.get("hasta") and dt.date.fromisoformat(s["hasta"]) < TODAY:
            continue
        out.append(s)
    return out


def sponsor_html(where):
    items = sponsors_for(where)
    if not items:
        return (f'<aside class="spon spon-vacio"><span class="tag">Espacio disponible</span>'
                f'<p>¿Tienes una herramienta de IA? Aparece destacada aquí. '
                f'<a href="{link("/patrocina/")}">Ver cómo</a></p></aside>')
    cards = []
    for s in items:
        cards.append(f'<aside class="spon"><span class="tag">Patrocinado</span>'
                     f'<p><strong>{ext(s["url"] + ("&" if "?" in s["url"] else "?") + "ref=queiauso", e(s["nombre"]), "")}</strong> · {e(s["texto"])}</p></aside>')
    return "".join(cards)


def analytics():
    gc = CFG.get("goatcounter")
    if not gc:
        return ""
    return (f'<script data-goatcounter="https://{e(gc)}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


AC = ' aria-current="page"'


def page(path, title, desc, body, jsonld=None, canonical=None, noindex=False):
    url = f"{BU}{path}"
    ld = ""
    for block in (jsonld or []):
        ld += f'<script type="application/ld+json">{json.dumps(block, ensure_ascii=False)}</script>\n'
    nav = "".join(
        f'<a href="{link(h)}"{AC if h == path else ""}>{t}</a>'
        for h, t in [("/", "Inicio"), ("/novedades/", "Novedades"), ("/patrocina/", "Patrocina"), ("/acerca/", "Cómo elegimos")]
    )
    cinta = "".join(f'<a href="{e(n["fuente"])}" target="_blank" rel="noopener"><b>{dt.date.fromisoformat(n["fecha"]).day} {MESES[dt.date.fromisoformat(n["fecha"]).month - 1][:3]}</b>{e(n["titulo"])}</a>'
                    for n in NEWS[:8])
    html_doc = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">{'<meta name="robots" content="noindex">' if noindex else ""}
<link rel="canonical" href="{e(canonical or url)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:locale" content="es_LA">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{e(CFG['nombre'])} · Novedades" href="{link('/feed.xml')}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23e8590c'/%3E%3Ctext x='16' y='23' font-size='20' text-anchor='middle' fill='white' font-family='Arial' font-weight='700'%3E%3F%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,400..900,0..100,0..1;1,9..144,400..900,0..100,0..1&family=IBM+Plex+Mono:wght@400;600&family=Instrument+Sans:wght@400..700&display=swap">
<link rel="stylesheet" href="{link('/assets/style.css')}">
<script>document.documentElement.classList.add('js')</script>
{ld}</head>
<body>
<header class="top"><div class="wrap">
<a class="logo" href="{link('/')}"><span class="q">¿</span>Qué IA Uso<span class="q">?</span></a>
<nav aria-label="Principal">{nav}</nav>
</div></header>
<div class="cinta" role="region" aria-label="Últimas novedades"><div class="cinta-in">{cinta}</div></div>
<main class="wrap">
{body}
</main>
<footer class="pie"><div class="wrap">
<p><a class="logo" href="{link('/')}"><span class="q">¿</span>Qué IA Uso<span class="q">?</span></a><br>{e(CFG['lema'])}</p>
<p>Actualizado el {fecha_larga(TODAY.isoformat())}. Los precios y planes cambian seguido: confírmalos en el sitio oficial antes de pagar.
Los espacios marcados «Patrocinado» son pagados y no cambian el orden de las recomendaciones. Las marcas pertenecen a sus dueños; este sitio no está afiliado a ellas.</p>
<p><a href="{link('/feed.xml')}">RSS</a> · <a href="{link('/llms.txt')}">llms.txt</a> · <a href="{link('/patrocina/')}">Patrocina</a> · <a href="{link('/acerca/')}">Cómo elegimos</a></p>
</div></footer>
<script src="{link('/assets/app.js')}" defer></script>
{analytics()}
</body>
</html>
"""
    target = OUT / path.lstrip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html_doc, encoding="utf-8")


def precio(t):
    if t.get("precio_desde_usd") is not None:
        p = t["precio_desde_usd"]
        p = str(int(p)) if float(p).is_integer() else f"{p:.2f}".rstrip("0").rstrip(".").replace(".", ",")
        nota = f" ({t['nota_precio']})" if t.get("nota_precio") else ""
        return f"desde USD {p}/mes{nota}"
    return "ver en su sitio"


def tool_card(t, rank, cat_id):
    badges = []
    if rank == 0:
        pass
    if t.get("plan_gratis"):
        badges.append(f'<span class="b b-free" title="{e(t.get("nota_gratis") or "")}">Plan gratis</span>')
    if t.get("espanol"):
        badges.append('<span class="b">En español</span>')
    pg = t.get("plan_gratis")
    if pg is True:
        nota = f'<li><strong>Plan gratis:</strong> {e(t.get("nota_gratis") or "sí")}</li>'
    elif pg is False:
        nota = f'<li><strong>Plan gratis:</strong> no{" · " + e(t["nota_gratis"]) if t.get("nota_gratis") else ""}</li>'
    else:
        nota = ""
    ver = f'<li><strong>Datos revisados:</strong> {fecha_larga(t["verificado"])}</li>' if t.get("verificado") else ""
    sello = '<span class="sello">Mejor opción</span>' if rank == 0 else ""
    precio_n = t.get("precio_desde_usd") if t.get("precio_desde_usd") is not None else ""
    if t.get("plan_gratis"):
        precio_n = 0
    return f"""<article class="tool" id="{e(slug(t['nombre']))}" data-rank="{rank}" data-free="{1 if t.get('plan_gratis') else 0}" data-precio="{precio_n}">
{sello}<span class="rank"><span class="sr">Puesto </span>{rank + 1}</span>
<div class="tool-h"><h3>{ext(t['url'], e(t['nombre']))}</h3><span class="maker">{e(t.get('empresa', ''))}</span></div>
<div class="badges">{''.join(badges)}</div>
<p class="best"><strong>Ideal para:</strong> {e(cap(t['mejor_para']))}</p>
<p>{e(t['veredicto'])}</p>
<ul class="meta">{nota}<li><strong>Precio:</strong> {precio(t)}</li>{ver}</ul>
</article>"""


def gratis_txt(t):
    return {True: "Sí", False: "No"}.get(t.get("plan_gratis"), "Ver en su sitio")


def cap(s):
    return s[:1].upper() + s[1:]


def slug(s):
    import re
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def free_tools(tools):
    return [t for t in tools if t.get("plan_gratis")]


def respuesta_corta(cat, tools):
    if not tools:
        return ""
    t0 = tools[0]
    txt = f"Usa <strong>{e(t0['nombre'])}</strong> para {e(t0['mejor_para'])}."
    gratis = [t for t in free_tools(tools) if t is not t0]
    if not t0.get("plan_gratis") and gratis:
        txt += f" Si quieres empezar gratis, prueba <strong>{e(gratis[0]['nombre'])}</strong>."
    elif len(tools) > 1:
        txt += f" La alternativa es <strong>{e(tools[1]['nombre'])}</strong>, para {e(tools[1]['mejor_para'])}."
    return txt


def faq(cat, tools):
    if not tools:
        return []
    t0 = tools[0]
    gratis = free_tools(tools)
    qa = [
        (f"¿Cuál es la mejor IA para {cat['tarea']} en {MES}?",
         f"{t0['nombre']}. {t0['veredicto']}"),
        (f"¿Hay alguna IA gratis para {cat['tarea']}?",
         ("Sí. " + " ".join(f"{t['nombre']}: {t.get('nota_gratis') or 'tiene plan gratis'}." for t in gratis))
         if gratis else "No encontramos una opción buena con plan gratis; todas las de esta lista son de pago o tienen solo prueba."),
    ]
    if len(tools) > 1:
        t1 = tools[1]
        qa.append((f"¿Qué alternativa hay a {t0['nombre']}?",
                   f"{t1['nombre']}, ideal para {t1['mejor_para']}. {t1['veredicto']}"))
    return qa


def build_category(cat):
    tools = TOOLS.get(cat["id"], [])
    title = f"¿Qué IA uso para {cat['tarea']}? ({MES_CORTO})"
    desc = recortar(f"Mejores IA para {cat['tarea']} en {MES_CORTO}: "
                    + ", ".join(t["nombre"] for t in tools[:3]) + ". Comparadas en español, con opciones gratis.")
    qa = faq(cat, tools)
    news = [n for n in NEWS if n.get("categoria") == cat["id"]][:5]
    news_html = ""
    if news:
        news_html = "<h2>Novedades recientes</h2><ul class='news'>" + "".join(
            f"<li><time>{fecha_larga(n['fecha'])}</time> {ext(n['fuente'], e(n['titulo']))}<span>{e(n['resumen'])}</span></li>"
            for n in news) + "</ul>"
    otras = "".join(f'<a class="chip" href="{link("/para/" + c["id"] + "/")}">{e(c["nombre"])}</a>'
                    for c in CATS if c["id"] != cat["id"])
    tabla = "".join(
        f"<tr><td>{ext(t['url'], e(t['nombre']))}</td><td>{e(t['mejor_para'])}</td>"
        f"<td>{gratis_txt(t)}</td><td>{precio(t)}</td></tr>" for t in tools)
    body = f"""
<nav class="miga"><a href="{link('/')}">Inicio</a> › {e(cat['nombre'])}</nav>
<h1>¿Qué IA uso para <span class="marca">{e(cat['tarea'])}</span>?</h1>
<p class="lead">{e(cat['intro'])}</p>
<div class="nota-adhesiva"><span class="tag">Respuesta corta · {MES}</span><p>{respuesta_corta(cat, tools)}</p></div>
{sponsor_html(cat['id'])}
<h2>Las {len(tools)} mejores, en orden</h2>
<div class="filtros" role="toolbar" aria-label="Filtrar y ordenar">
<button type="button" data-f="gratis" aria-pressed="false">Solo con plan gratis</button>
<button type="button" data-f="rank" aria-pressed="true">Orden recomendado</button>
<button type="button" data-f="precio" aria-pressed="false">Más baratas primero</button>
<span id="cuenta" aria-live="polite">{len(tools)} herramientas</span>
</div>
<div class="tools">{''.join(tool_card(t, i, cat['id']) for i, t in enumerate(tools))}</div>
<p id="vacio" class="vacio" hidden>Ninguna herramienta de esta tarea tiene plan gratis. Quita el filtro para ver todas.</p>
<h2>Comparación rápida</h2>
<div class="tabla" tabindex="0" role="region" aria-label="Tabla comparativa"><table><thead><tr><th>Herramienta</th><th>Ideal para</th><th>Plan gratis</th><th>Precio</th></tr></thead><tbody>{tabla}</tbody></table></div>
{news_html}
<h2>Preguntas frecuentes</h2>
{''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in qa)}
<h2>Otras tareas</h2>
<div class="chips">{otras}</div>
"""
    ld = [
        {"@context": "https://schema.org", "@type": "ItemList",
         "name": f"Mejores IA para {cat['tarea']}",
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": t["nombre"], "url": t["url"]}
                             for i, t in enumerate(tools)]},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Inicio", "item": BU + "/"},
                             {"@type": "ListItem", "position": 2, "name": cat["nombre"], "item": f"{BU}/para/{cat['id']}/"}]},
    ]
    page(f"/para/{cat['id']}/", title, desc, body, ld)


def build_home():
    rots = [-1.4, 1.1, -0.6, 1.6, -1.0, 0.5, 1.3, -1.7]
    cards = []
    for i, c in enumerate(CATS):
        tools = TOOLS.get(c["id"], [])
        top = tools[0]["nombre"] if tools else "—"
        gratis = next((t["nombre"] for t in tools if t.get("plan_gratis")), None)
        if tools and tools[0].get("plan_gratis"):
            g = '<span class="free">✓ Tiene plan gratis</span>'
        else:
            g = f'<span class="free">Gratis: {e(gratis)}</span>' if gratis else ""
        cards.append(f'<a class="cat" style="--rot:{rots[i % len(rots)]}deg" href="{link("/para/" + c["id"] + "/")}" data-id="{c["id"]}">'
                     f'<span class="cat-q">para {e(c["tarea"])}</span>'
                     f'<strong>{e(top)}</strong>{g}<span class="ir" aria-hidden="true">→</span></a>')

    def mini(t):
        return {"n": t["nombre"], "m": t["mejor_para"], "u": t["url"]} if t else None

    idx = []
    for c in CATS:
        tools = TOOLS.get(c["id"], [])
        idx.append({"id": c["id"], "t": c["tarea"], "n": c["nombre"], "k": KEYS.get(c["id"], []),
                    "h": [t["nombre"] for t in tools], "url": link("/para/" + c["id"] + "/"),
                    "top": mini(tools[0] if tools else None),
                    "g": mini(next((t for t in tools if t.get("plan_gratis")), None))})
    news = "".join(
        f"<li><time>{fecha_larga(n['fecha'])}</time> {ext(n['fuente'], e(n['titulo']))}<span>{e(n['resumen'])}</span></li>"
        for n in NEWS[:6])
    total = len({t["nombre"] for v in TOOLS.values() for t in v})
    gratis_n = len({t["nombre"] for v in TOOLS.values() for t in v if t.get("plan_gratis")})
    ejemplos = ["hacer un logo", "transcribir una reunión", "responder WhatsApp", "crear un video para TikTok",
                "armar una presentación", "estudiar para una prueba", "programar una app", "clonar mi voz"]
    atajos = [("📹 Video", "video"), ("🎨 Logo", "logo"), ("💬 WhatsApp", "whatsapp"), ("📊 Excel", "excel"),
              ("🎙️ Voz", "voz"), ("📚 Estudiar", "estudiar"), ("💻 Programar", "programar")]
    datos_json = json.dumps(idx, ensure_ascii=False).replace("</", "<\\/")
    test_ops = "".join(f'<button type="button" data-cat="{c["id"]}">{e(c["nombre"])}</button>' for c in CATS)
    body = f"""
<section class="hero">
<p class="kicker">Directorio en español · revisado cada día</p>
<h1>¿Qué <span class="marca">IA</span> uso?</h1>
<div class="frase">
<label for="q">Necesito una IA para</label>
<span class="hueco"><input id="q" type="search" autocomplete="off" enterkeyhint="go" placeholder="hacer un logo"
 data-ejemplos='{e(json.dumps(ejemplos, ensure_ascii=False))}'></span>
</div>
<div class="atajos" aria-label="Búsquedas rápidas">{''.join(f'<button type="button" data-q="{e(q)}">{e(t)}</button>' for t, q in atajos)}</div>
<p id="sin" class="sin" role="status" hidden>Mmm, esa no la tenemos todavía. Prueba con otra palabra o elige una ficha.</p>
<div class="stats">
<span><strong data-count="{total}">{total}</strong>herramientas revisadas</span>
<span><strong data-count="{len(CATS)}">{len(CATS)}</strong>tareas</span>
<span><strong data-count="{gratis_n}">{gratis_n}</strong>con plan gratis</span>
</div>
</section>
<h2 class="sr">Tareas</h2>
<div class="cats" id="cats">{''.join(cards)}</div>
<section class="test" id="test" aria-label="Test para elegir una IA">
<div class="barra" aria-hidden="true"><i></i></div>
<div class="paso">
<p class="kicker">¿No sabes qué buscar?</p>
<h2>Te lo resolvemos en 2 clics</h2>
<p>1. ¿Qué quieres hacer?</p>
<div class="ops">{test_ops}</div>
</div>
<div class="paso">
<p class="kicker">Paso 2 de 2</p>
<h2>¿Quieres pagar?</h2>
<div class="ops"><button type="button" data-plata="gratis">Solo gratis, por ahora</button><button type="button" data-plata="pago">Pago si vale la pena</button></div>
</div>
<div class="paso">
<p class="kicker">Tu IA es…</p>
<div class="resultado" aria-live="polite">
<p class="gana">—</p>
<p class="por"></p>
<a class="btn sitio" href="#" target="_blank" rel="noopener">Ir al sitio ↗</a>
<a class="ficha" href="#">Ver todas las opciones →</a>
<button type="button" class="volver">↺ Empezar de nuevo</button>
</div>
</div>
</section>
{sponsor_html('portada')}
<h2>Lo último en IA</h2>
<ul class="news">{news}</ul>
<p><a href="{link('/novedades/')}">Ver todas las novedades →</a></p>
<script type="application/json" id="datos">{datos_json}</script>
"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": CFG["nombre"], "url": BU + "/",
           "inLanguage": "es", "description": CFG["lema"]}]
    page("/", f"¿Qué IA uso? La IA correcta para cada tarea ({MES_CORTO})",
         f"Qué IA usar para cada tarea, en español: programar, imágenes, video, voz, WhatsApp, Excel y más, con opciones gratis. Actualizado en {MES_CORTO}.",
         body, ld)


def build_news():
    items = "".join(
        f"<li id='{e(slug(n['fecha'] + '-' + n['titulo']))[:80]}'><time>{fecha_larga(n['fecha'])}</time> "
        f"{ext(n['fuente'], e(n['titulo']))}<span>{e(n['resumen'])}</span></li>" for n in NEWS)
    body = f"""<nav class="miga"><a href="{link('/')}">Inicio</a> › Novedades</nav>
<h1>Novedades de herramientas de IA</h1>
<p class="lead">Lanzamientos y cambios importantes, resumidos en español con el enlace a la fuente. Suscríbete por <a href="{link('/feed.xml')}">RSS</a>.</p>
{sponsor_html('novedades')}
<ul class="news">{items}</ul>"""
    page("/novedades/", f"Novedades de IA en español ({MES})",
         "Lanzamientos y actualizaciones de herramientas de inteligencia artificial, resumidos en español con su fuente.", body)


def build_sponsor():
    cfg = CFG
    email = cfg.get("contacto_email")
    issue = f"https://github.com/{cfg['repo']}/issues/new?title=Quiero+patrocinar&labels=patrocinio"
    contacto = (f'<a class="btn" href="mailto:{e(email)}?subject=Patrocinio%20Qu%C3%A9%20IA%20Uso">Escríbenos</a>'
                if email else f'<a class="btn" href="{e(issue)}" target="_blank" rel="noopener">Escríbenos</a>')

    def pago(key):
        u = cfg.get(key)
        prov = cfg.get("pago_proveedor") or "tarjeta"
        return (f'<p><a class="btn btn-2" href="{e(u)}" target="_blank" rel="noopener">Suscribirme con {e(prov)}</a></p>'
                f'<p class="nota">Cobro mensual automático; lo cancelas cuando quieras.</p>') if u else ""

    def monto(n):
        if cfg.get("moneda", "CLP") == "CLP":
            return f"${n:,.0f}".replace(",", ".") + "<span> CLP/mes</span>"
        return f"USD {n}<span>/mes</span>"

    body = f"""<nav class="miga"><a href="{link('/')}">Inicio</a> › Patrocina</nav>
<h1>Ponte frente a quien <span class="marca">está eligiendo</span></h1>
<p class="lead">Llega a personas que están decidiendo qué herramienta de IA usar, en español, justo en el momento de elegir.</p>
<div class="planes">
<div class="plan"><h2>Destacado en una tarea</h2><p class="precio">{monto(cfg['precio_destacado_categoria'])}</p>
<p>Tu herramienta en un recuadro «Patrocinado» arriba de la lista de la tarea que elijas (por ejemplo, «para crear videos»).</p>{pago('pago_destacado_categoria')}</div>
<div class="plan"><h2>Portada y novedades</h2><p class="precio">{monto(cfg['precio_destacado_portada'])}</p>
<p>Recuadro en la portada y en la página de novedades{", más una mención en el boletín" if cfg.get("newsletter_url") else ""}.</p>{pago('pago_destacado_portada')}</div>
</div>
<p>Los patrocinios van siempre marcados y <strong>no cambian el orden</strong> de las recomendaciones: eso es lo que hace que la gente confíe en la lista.</p>
<p>¿Dudas o quieres otro formato? {contacto}</p>
<div id="gracias" class="corta" hidden><span class="tag">Pago recibido</span><p>¡Gracias! Escríbenos con el nombre y la web de tu herramienta, y la publicamos en menos de 48 horas.</p></div>
"""
    page("/patrocina/", "Patrocina Qué IA Uso", "Muestra tu herramienta de IA a público hispanohablante que está eligiendo qué usar.", body)


def build_about():
    body = f"""<nav class="miga"><a href="{link('/')}">Inicio</a> › Cómo elegimos</nav>
<h1>Cómo elegimos las herramientas</h1>
<p class="lead">Qué IA Uso es un directorio independiente, escrito en español para Latinoamérica y España. No recibe dinero de las herramientas por el orden en que aparecen.</p>
<h2>Transparencia</h2>
<p>Las fichas las prepara y actualiza un agente de IA (Claude, de Anthropic) que busca y verifica la información en las páginas oficiales, y una persona revisa los cambios importantes. Como Claude también aparece en el directorio, sus fichas se evalúan con los mismos criterios que las demás; si crees que alguna recomendación está sesgada, avísanos.</p>
<h2>Criterios</h2>
<ul class="lista">
<li><strong>Calidad del resultado</strong> para la tarea concreta, no en general.</li>
<li><strong>Si funciona en español</strong>: entiende instrucciones en español y entrega resultados naturales.</li>
<li><strong>Plan gratis o precio de entrada</strong> razonable, verificado en la página oficial de precios.</li>
<li><strong>Facilidad</strong> para alguien que no es técnico.</li>
</ul>
<h2>Actualización</h2>
<p>La lista se revisa todos los días con ayuda de un agente de IA que busca lanzamientos nuevos, y una persona aprueba los cambios grandes. Cada herramienta tiene la fecha en que se verificó. Si ves un dato malo, <a href="https://github.com/{CFG['repo']}/issues/new?title=Dato+incorrecto" target="_blank" rel="noopener">avísanos aquí</a>.</p>
<h2>Patrocinios</h2>
<p>Los espacios pagados dicen «Patrocinado» y nunca cambian el orden de las recomendaciones.</p>"""
    page("/acerca/", "Cómo elegimos las herramientas · Qué IA Uso",
         "Criterios y método de actualización del directorio Qué IA Uso.", body)


def build_404():
    body = f"""<p class="kicker">Error 404</p><h1>Ni la IA encontró <span class="marca">esta página</span></h1><p class="lead">Vuelve a la <a href="{link('/')}">portada</a> y busca tu tarea.</p>"""
    page("/404.html", "Página no encontrada · Qué IA Uso", "Página no encontrada.", body, noindex=True)


def build_llms():
    lines = [f"# {CFG['nombre']}", "", f"> {CFG['lema']} Directorio en español de herramientas de IA ordenadas por tarea, actualizado en {MES}.", ""]
    lines.append("## Tareas")
    for c in CATS:
        tools = TOOLS.get(c["id"], [])
        lines.append(f"- [¿Qué IA uso para {c['tarea']}?]({BU}/para/{c['id']}/): " + ", ".join(t["nombre"] for t in tools[:5]))
    lines += ["", "## Otros", f"- [Novedades]({BU}/novedades/)", f"- [Texto completo]({BU}/llms-full.txt)", f"- [Cómo elegimos]({BU}/acerca/)"]
    (OUT / "llms.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    full = [f"# {CFG['nombre']} — texto completo ({MES})", ""]
    for c in CATS:
        tools = TOOLS.get(c["id"], [])
        full += [f"## ¿Qué IA uso para {c['tarea']}?", f"URL: {BU}/para/{c['id']}/", "", c["intro"], ""]
        for i, t in enumerate(tools):
            g = f" Plan gratis: {t.get('nota_gratis') or 'sí'}." if t.get("plan_gratis") else " Sin plan gratis."
            full.append(f"{i + 1}. **{t['nombre']}** ({t['url']}) — Ideal para: {t['mejor_para']}. {t['veredicto']}{g} Precio: {precio(t)}.")
        full.append("")
    full.append("## Novedades")
    for n in NEWS[:30]:
        full.append(f"- {n['fecha']}: {n['titulo']} — {n['resumen']} ({n['fuente']})")
    (OUT / "llms-full.txt").write_text("\n".join(full) + "\n", encoding="utf-8")


def build_seo_files():
    urls = ["/", "/novedades/", "/patrocina/", "/acerca/"] + [f"/para/{c['id']}/" for c in CATS]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append(f"<url><loc>{BU}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>")
    sm.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BU}/sitemap.xml\n", encoding="utf-8")

    from email.utils import format_datetime
    items = []
    for n in NEWS[:40]:
        d = dt.datetime.fromisoformat(n["fecha"] + "T12:00:00+00:00")
        items.append(f"<item><title>{e(n['titulo'])}</title><link>{e(n['fuente'])}</link>"
                     f"<guid isPermaLink=\"false\">{e(n['fecha'] + '-' + slug(n['titulo']))}</guid>"
                     f"<pubDate>{format_datetime(d)}</pubDate><description>{e(n['resumen'])}</description></item>")
    rss = (f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
           f"<title>{e(CFG['nombre'])} · Novedades de IA</title><link>{BU}/novedades/</link>"
           f"<description>Novedades de herramientas de IA en español</description><language>es</language>"
           f'<atom:link href="{BU}/feed.xml" rel="self" type="application/rss+xml"/>'
           f"<lastBuildDate>{format_datetime(dt.datetime.now(dt.timezone.utc))}</lastBuildDate>"
           + "".join(items) + "</channel></rss>")
    (OUT / "feed.xml").write_text(rss, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ASSETS, OUT / "assets")
    for f in (ROOT / "static").glob("*"):
        shutil.copy(f, OUT / f.name)  # archivos de verificación (Google, etc.) en la raíz
    build_home()
    for c in CATS:
        build_category(c)
    build_news()
    build_sponsor()
    build_about()
    build_404()
    build_llms()
    build_seo_files()
    n = sum(1 for _ in OUT.rglob("*.html"))
    print(f"OK: {n} páginas, {sum(len(v) for v in TOOLS.values())} herramientas, {len(NEWS)} novedades → {OUT}")


if __name__ == "__main__":
    main()
