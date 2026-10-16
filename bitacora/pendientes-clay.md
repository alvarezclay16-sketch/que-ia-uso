# Pendientes de Clay

Lo que el bot necesita de ti para ganar plata. Nada de esto es urgente; el sitio funciona sin ello.

- [ ] **Correo de contacto para patrocinadores** (16-oct: Clay decidió ninguno por ahora) (va a `data/config.json` → `contacto_email`). Mientras no exista, el botón «Escríbenos» abre un formulario en GitHub.
- [ ] **Cobros con Mercado Pago (Chile)**: en https://www.mercadopago.cl/herramientas-para-vender/suscripciones crea 2 planes mensuales:
  - «Qué IA Uso · Destacado en una tarea» a $45.000 CLP/mes
  - «Qué IA Uso · Portada y novedades» a $90.000 CLP/mes
  - Si te pide URL de retorno, pon: https://alvarezclay16-sketch.github.io/que-ia-uso/patrocina/?gracias=1
  - Pásale los 2 links al bot (o pégalos en `data/config.json` → `pago_destacado_categoria` y `pago_destacado_portada`).
  - Boleta o factura: emítela tú (SII o btools) cuando entre un pago; el bot no factura.
- [ ] **Stripe (cuenta creada como EE. UU.)**: no sirve para cobrar desde Chile. Ciérrala en el panel de Stripe si no la vas a usar (las claves de prueba quedaron solo en `.env` local, fuera de GitHub).
- [ ] **Analítica** (para saber si llega gente): crear una cuenta gratis en goatcounter.com y poner el código en `config.json` → `goatcounter`.
- [x] **Google Search Console**: hecho el 16-oct con alvarez.clay16@gmail.com (verificado con static/google38a4cf67a49f016a.html, no borrar) y sitemap enviado.
- [ ] **Boletín** (opcional, después): cuenta en Resend o Buttondown cuando haya visitas.
- [ ] **Difusión** (16-oct: post publicado en LinkedIn; X pendiente porque Chrome no tiene sesión iniciada en X; textos en bitacora/difusion-posts.md): es lo único que el bot no puede hacer solo. Compartir el link en X, LinkedIn o grupos de WhatsApp de vez en cuando.
