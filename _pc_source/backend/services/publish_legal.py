"""Páginas legales reales del sitio estático (A8 de la auditoría).

Texto sobrio en español, sin claims, sin datos de contacto inventados (se usa
"el correo del recibo de compra"). Separado de `publish_content.py` para
respetar el límite de 250 líneas.
"""

from backend.services.publish_content import LEGAL_PAGES, _legal_links, _shell, esc

LEGAL_DOCS = {
    "terminos": {
        "title": "Términos de uso",
        "intro": "Estos términos describen la compra y el uso de los productos digitales de este sitio.",
        "blocks": [
            ("Objeto", ["Se venden archivos digitales de formación y herramientas (PDF, HTML, plantillas y "
                        "paquetes). No se venden servicios personalizados ni asesoría financiera.",
                        "Los precios se muestran en USD; el precio local en COP es una referencia y la "
                        "conversión final la aplica la pasarela de pago."]),
            ("Aceptación y entrega", ["Al pagar aceptas estos términos. La entrega es digital, mediante el "
                                      "archivo o enlace que entrega la pasarela, sin envío físico.",
                                      "Si el archivo no llega, escribe al correo que aparece en el recibo de compra."]),
            ("Uso permitido", ["Se concede una licencia personal, no transferible, para usar el material "
                               "en tus propios proyectos. No se permite su reventa, redistribución pública "
                               "ni publicación como producto propio."]),
            ("Límites de responsabilidad", ["El contenido no garantiza ingresos, ventas ni resultados. "
                                            "Cada comprador es responsable de aplicar el material en su contexto "
                                            "y de cumplir las normas de su país y de las plataformas que use."]),
            ("Cambios", ["Estos términos pueden actualizarse. La fecha de la última actualización aparece "
                         "al final de la página. Las compras ya realizadas se rigen por la versión vigente "
                         "en el momento del pago."]),
            ("Ley aplicable", ["Estos términos se interpretan conforme a la legislación de la República de "
                               "Colombia, sin perjuicio de los derechos del consumidor de tu país."]),
        ],
    },
    "privacidad": {
        "title": "Política de privacidad y datos personales",
        "intro": "Esta política explica qué datos personales se tratan y para qué, conforme a la Ley 1581 de 2012 de Colombia.",
        "blocks": [
            ("Datos que se tratan", ["Correo electrónico, nombre y datos de la compra. Los datos de la tarjeta "
                                     "los procesa la pasarela de pago (Gumroad o Hotmart); este sitio no los almacena."]),
            ("Finalidad", ["Entregar el producto, dar soporte, enviar actualizaciones de la versión comprada "
                           "y atender solicitudes de reembolso o derechos de datos."]),
            ("No venta a terceros", ["No se venden ni se comparten datos personales con terceros distintos de "
                                     "los proveedores necesarios para procesar el pago y entregar el archivo."]),
            ("Conservación y derechos", ["Los datos se conservan mientras exista la relación comercial y el plazo "
                                         "legal aplicable. Puedes solicitar acceso, corrección, actualización o "
                                         "supresión escribiendo al correo del recibo de compra.",
                                         "La solicitud se atiende en los términos de la Ley 1581 de 2012."]),
            ("Cookies", ["El sitio estático no usa cookies de seguimiento publicitario. Las pasarelas aplican "
                         "sus propias políticas cuando sales de este dominio para pagar."]),
        ],
    },
    "reembolso": {
        "title": "Política de reembolsos",
        "intro": "Los productos son digitales y la política se aplica junto con la de la pasarela con la que pagaste.",
        "blocks": [
            ("Regla general", ["Solicita el reembolso dentro del plazo que fija la pasarela de pago. "
                               "Gumroad y Hotmart aplican su propia política y sus tiempos de procesamiento."]),
            ("Cómo solicitarlo", ["Escribe al correo que aparece en el recibo de compra con el número de "
                                  "pedido, el SKU y el motivo. Se responde con el estado de la solicitud."]),
            ("Casos", ["Si el archivo no se entregó o está dañado, se corrige la entrega o se reembolsa.",
                       "Los reembolsos se procesan por el mismo medio de pago de la compra."]),
            ("Derechos del consumidor", ["Nada en esta política limita los derechos que la ley de tu país "
                                         "reconozca al consumidor."]),
        ],
    },
    "licencia": {
        "title": "Licencia de uso",
        "intro": "La compra otorga una licencia personal de uso del material, no la propiedad intelectual.",
        "blocks": [
            ("Alcance", ["Puedes usar los archivos en tus propios proyectos, personales o comerciales, "
                         "y modificarlos para tu operación."]),
            ("Restricciones", ["No puedes revender el archivo original ni una versión modificada como producto "
                               "propio, ni redistribuirlo públicamente, ni cederlo a terceros como si fuera tuyo.",
                               "No se permite usar el material para prometer resultados garantizados a terceros."]),
            ("Duración", ["La licencia es perpetua para la versión comprada. Las actualizaciones se entregan "
                          "según lo indicado en la página del producto."]),
            ("Contacto", ["Dudas sobre la licencia: escribe al correo que aparece en el recibo de compra."]),
        ],
    },
}


def build_legal_html(slug: str, generated_at: str) -> str:
    doc = LEGAL_DOCS[slug]
    blocks = []
    for heading, paragraphs in doc["blocks"]:
        body = "".join(f"<p>{esc(text)}</p>" for text in paragraphs)
        blocks.append(f"<h2>{esc(heading)}</h2>{body}")
    body = (
        '<a class="back" href="../../">Volver a la tienda</a>'
        f'<article><h1>{esc(doc["title"])}</h1><p class="lead">{esc(doc["intro"])}</p>'
        f'{"".join(blocks)}<p class="note">Última actualización: {esc(generated_at)}. '
        "Contacto: el correo que aparece en el recibo de compra.</p></article>"
    )
    footer = f"Ronin Ventas OS · documento legal del sitio estático.{_legal_links('../../legal/', '../../')}"
    return _shell(f'{doc["title"]} — Ronin Ventas OS', body, footer)


def build_legal_index(generated_at: str) -> str:
    cards = "".join(
        f'<div class="card" style="padding:16px"><h3><a href="{slug}/" style="color:inherit">'
        f'{esc(label)}</a></h3><p>{esc(LEGAL_DOCS[slug]["intro"])}</p></div>'
        for slug, label in LEGAL_PAGES
    )
    body = (
        '<a class="back" href="../">Volver a la tienda</a>'
        f'<h1>Documentos legales</h1><p class="lead">Cuatro documentos vigentes del sitio. '
        f"Última actualización: {esc(generated_at)}.</p>"
        f'<div class="grid" style="margin-top:20px">{cards}</div>'
    )
    footer = f"Ronin Ventas OS · contacto: el correo del recibo de compra.{_legal_links('', '../')}"
    return _shell("Legal — Ronin Ventas OS", body, footer)
