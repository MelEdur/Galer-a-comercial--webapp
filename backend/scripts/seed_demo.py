"""Idempotent demo data for the shopping gallery.

Run from ``backend/`` with::

    python -m scripts.seed_demo

It creates one merchant per store, fills the store public information
(description, logo, contact, hours and links) and adds a catalog of 20
products per store: three curated products plus 17 deterministic variants
generated from the store categories. Running it again updates the demo stores
and products instead of duplicating them.

Demo merchant accounts use the same password: ``comercio1234``.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import time
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from urllib.parse import quote_plus

from sqlalchemy import select

import app.db.registry  # noqa: F401  (registers all models / relationship targets)
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.accounts.models import User
from app.modules.catalog.models import (
    Category,
    Product,
    ProductCategory,
    ProductImage,
)
from app.modules.stores.models import Store, StoreHour, StoreLink

DEMO_PASSWORD = "comercio1234"

# (name, description, price, offer_price or None, category names)
ProductSpec = tuple[str, str, str, str | None, list[str]]

STORES: list[dict[str, object]] = [
    {
        "number": 1,
        "name": "Moda Urbana",
        "description": "Indumentaria urbana y accesorios para todos los días.",
        "color": "4f46e5",
        "hours": "shop",
        "products": [
            ("Remera oversize negra", "Algodón peinado, corte holgado.", "15900.00", "12900.00", ["Indumentaria"]),
            ("Jean recto azul", "Denim rígido con lavado medio.", "34900.00", None, ["Indumentaria"]),
            ("Gorra urbana", "Gorra ajustable con bordado frontal.", "9900.00", None, ["Accesorios"]),
        ],
    },
    {
        "number": 2,
        "name": "Café Central",
        "description": "Cafetería de especialidad y panadería artesanal.",
        "color": "b45309",
        "hours": "cafe",
        "products": [
            ("Café latte grande", "Espresso doble con leche vaporizada.", "3500.00", None, ["Gastronomía"]),
            ("Medialunas de manteca x6", "Recién horneadas, masa hojaldrada.", "4800.00", "3900.00", ["Gastronomía"]),
            ("Sándwich de jamón y queso", "Pan ciabatta tostado.", "5200.00", None, ["Gastronomía"]),
        ],
    },
    {
        "number": 3,
        "name": "TecnoStore",
        "description": "Tecnología, accesorios y periféricos para tu setup.",
        "color": "0f766e",
        "hours": "shop",
        "products": [
            ("Auriculares inalámbricos", "Bluetooth 5.3 con cancelación de ruido.", "45900.00", "39900.00", ["Tecnología"]),
            ("Teclado mecánico", "Switch rojo y retroiluminación RGB.", "62900.00", None, ["Tecnología"]),
            ("Mouse gamer", "Sensor óptico de 12.000 DPI.", "28900.00", None, ["Tecnología"]),
        ],
    },
    {
        "number": 4,
        "name": "Calzado Sur",
        "description": "Calzado cómodo para running, ciudad y verano.",
        "color": "7c2d12",
        "hours": "shop",
        "products": [
            ("Zapatillas running", "Amortiguación media y malla transpirable.", "78900.00", "65900.00", ["Calzado"]),
            ("Botas de cuero", "Cuero vacuno con suela antideslizante.", "99900.00", None, ["Calzado"]),
            ("Sandalias verano", "Plantilla acolchada y tiras ajustables.", "25900.00", None, ["Calzado"]),
        ],
    },
    {
        "number": 5,
        "name": "Belleza Natural",
        "description": "Cuidado facial y maquillaje con ingredientes suaves.",
        "color": "be185d",
        "hours": "shop",
        "products": [
            ("Crema facial hidratante", "Ácido hialurónico y aloe vera.", "18900.00", None, ["Belleza"]),
            ("Sérum vitamina C", "Ilumina y unifica el tono.", "24500.00", "19900.00", ["Belleza"]),
            ("Labial mate", "Larga duración, tono nude.", "8900.00", None, ["Belleza"]),
        ],
    },
    {
        "number": 6,
        "name": "Hogar & Deco",
        "description": "Textiles, iluminación y detalles para tu casa.",
        "color": "a16207",
        "hours": "shop",
        "products": [
            ("Juego de sábanas queen", "Algodón 300 hilos, cuatro piezas.", "45900.00", None, ["Hogar"]),
            ("Lámpara de mesa", "Base de madera y pantalla de lino.", "32900.00", "27900.00", ["Hogar"]),
            ("Set de tazas", "Cuatro tazas de cerámica esmaltada.", "15900.00", None, ["Hogar"]),
        ],
    },
    {
        "number": 7,
        "name": "Deportes Pro",
        "description": "Equipamiento y accesorios para entrenar mejor.",
        "color": "166534",
        "hours": "shop",
        "products": [
            ("Pelota de fútbol", "Número 5, costura reforzada.", "22900.00", None, ["Deportes"]),
            ("Mancuernas 5 kg", "Par con recubrimiento antideslizante.", "35900.00", "29900.00", ["Deportes"]),
            ("Botella deportiva", "1 litro, libre de BPA.", "9900.00", None, ["Deportes"]),
        ],
    },
    {
        "number": 8,
        "name": "Juguetería Fantasía",
        "description": "Juguetes, bloques y diversión para todas las edades.",
        "color": "7e22ce",
        "hours": "shop",
        "products": [
            ("Peluche gigante", "Oso de 80 cm, tela extra suave.", "25900.00", None, ["Juguetería"]),
            ("Set de bloques", "120 piezas de construcción.", "31900.00", "25900.00", ["Juguetería"]),
            ("Auto a control remoto", "Tracción 4x4 y batería recargable.", "45900.00", None, ["Juguetería"]),
        ],
    },
    {
        "number": 9,
        "name": "Librería Cultura",
        "description": "Libros, agendas y papelería para lectores curiosos.",
        "color": "1e40af",
        "hours": "shop",
        "products": [
            ("Novela best seller", "Última edición en tapa blanda.", "18900.00", None, ["Librería"]),
            ("Agenda 2027", "Formato A5 con separadores.", "12900.00", None, ["Librería"]),
            ("Set de marcadores", "Seis colores con punta fina.", "4900.00", "3900.00", ["Librería"]),
        ],
    },
    {
        "number": 10,
        "name": "Accesorios Chic",
        "description": "Carteras, joyería y relojes con estilo propio.",
        "color": "9d174d",
        "hours": "shop",
        "products": [
            ("Cartera de cuero", "Cuero sintético con correa ajustable.", "45900.00", "37900.00", ["Accesorios"]),
            ("Collar dorado", "Baño de oro 18k, cadena fina.", "15900.00", None, ["Accesorios"]),
            ("Reloj minimalista", "Malla de acero y esfera blanca.", "38900.00", None, ["Accesorios"]),
        ],
    },
    {
        "number": 11,
        "name": "Moda Kids",
        "description": "Ropa, calzado y mochilas para los más chicos.",
        "color": "0284c7",
        "hours": "shop",
        "products": [
            ("Conjunto infantil", "Buzo y pantalón de algodón.", "22900.00", None, ["Indumentaria"]),
            ("Zapatillas niños", "Cierre velcro y suela flexible.", "27900.00", "22900.00", ["Calzado"]),
            ("Mochila escolar", "Dos compartimentos y espalda acolchada.", "18900.00", None, ["Accesorios"]),
        ],
    },
    {
        "number": 12,
        "name": "Óptica Visión",
        "description": "Anteojos de sol, recetados y accesorios de cuidado.",
        "color": "0e7490",
        "hours": "shop",
        "products": [
            ("Anteojos de sol", "Protección UV400, marco liviano.", "25900.00", None, ["Accesorios"]),
            ("Gafas recetadas", "Armazón metálico con cristales claros.", "45900.00", "38900.00", ["Accesorios"]),
            ("Estuche rígido", "Interior forrado y cierre magnético.", "6900.00", None, ["Accesorios"]),
        ],
    },
    {
        "number": 13,
        "name": "Perfumería Aroma",
        "description": "Fragancias, body splashes y aromas para el hogar.",
        "color": "9333ea",
        "hours": "shop",
        "products": [
            ("Perfume floral 100 ml", "Notas de jazmín y vainilla.", "55900.00", "47900.00", ["Belleza"]),
            ("Body splash", "Frescura cítrica de larga duración.", "18900.00", None, ["Belleza"]),
            ("Vela aromática", "Cera de soja con aroma a lavanda.", "12900.00", None, ["Hogar"]),
        ],
    },
    {
        "number": 14,
        "name": "Mundo Gamer",
        "description": "Consolas, accesorios y sillas para jugar cómodo.",
        "color": "1e293b",
        "hours": "shop",
        "products": [
            ("Consola portátil", "Pantalla OLED y 256 GB de almacenamiento.", "459900.00", None, ["Tecnología"]),
            ("Joystick inalámbrico", "Conexión Bluetooth y batería de 20 horas.", "65900.00", "55900.00", ["Tecnología"]),
            ("Silla gamer", "Reclinable con apoyabrazos ajustables.", "189900.00", None, ["Hogar"]),
        ],
    },
    {
        "number": 15,
        "name": "Bazar Central",
        "description": "Artículos prácticos para cocina y organización.",
        "color": "c2410c",
        "hours": "shop",
        "products": [
            ("Organizador de cocina", "Tres niveles apilables.", "12900.00", None, ["Hogar"]),
            ("Set de ollas", "Cinco piezas antiadherentes.", "68900.00", "58900.00", ["Hogar"]),
            ("Espejo de pared", "Marco de madera, 60 x 80 cm.", "22900.00", None, ["Hogar"]),
        ],
    },
    {
        "number": 16,
        "name": "Ropa Deportiva Fit",
        "description": "Indumentaria técnica para entrenamiento diario.",
        "color": "15803d",
        "hours": "shop",
        "products": [
            ("Calza deportiva", "Tejido compresivo y cintura alta.", "24900.00", None, ["Indumentaria", "Deportes"]),
            ("Remera técnica", "Secado rápido y costuras planas.", "19900.00", "15900.00", ["Indumentaria", "Deportes"]),
            ("Campera rompeviento", "Liviana, con capucha y bolsillos.", "45900.00", None, ["Indumentaria"]),
        ],
    },
    {
        "number": 17,
        "name": "Panadería Delicias",
        "description": "Panes de masa madre, tortas y facturas del día.",
        "color": "b91c1c",
        "hours": "cafe",
        "products": [
            ("Pan artesanal", "Masa madre, corteza crocante.", "3500.00", None, ["Gastronomía"]),
            ("Torta de chocolate", "Bizcochuelo húmedo y ganache.", "12900.00", "9900.00", ["Gastronomía"]),
            ("Chipá x6", "Queso cremoso y tapioca.", "4200.00", None, ["Gastronomía"]),
        ],
    },
    {
        "number": 18,
        "name": "Zapatillas Plus",
        "description": "Zapatillas urbanas, skate y accesorios.",
        "color": "4338ca",
        "hours": "shop",
        "products": [
            ("Zapatillas urbanas", "Suela de goma y capellada de lona.", "69900.00", None, ["Calzado"]),
            ("Zapatillas skate", "Refuerzo lateral y plantilla acolchada.", "58900.00", "49900.00", ["Calzado"]),
            ("Medias deportivas", "Pack de tres pares de algodón.", "5900.00", None, ["Accesorios"]),
        ],
    },
    {
        "number": 19,
        "name": "Juguetes Educativos",
        "description": "Juegos de ingenio, ciencias y mesa para aprender.",
        "color": "6d28d9",
        "hours": "shop",
        "products": [
            ("Rompecabezas 500 piezas", "Paisaje ilustrado, piezas grandes.", "15900.00", None, ["Juguetería"]),
            ("Kit de ciencias", "Experimentos seguros para niños.", "32900.00", "27900.00", ["Juguetería", "Librería"]),
            ("Juego de mesa familiar", "Partidas de 30 a 60 minutos.", "24900.00", None, ["Juguetería"]),
        ],
    },
    {
        "number": 20,
        "name": "Librería Escolar",
        "description": "Todo para el ciclo escolar y la oficina.",
        "color": "0369a1",
        "hours": "shop",
        "products": [
            ("Mochila con ruedas", "Estructura reforzada y asa telescópica.", "38900.00", None, ["Accesorios", "Librería"]),
            ("Cartuchera completa", "Dos compartimentos y accesorios.", "14900.00", "11900.00", ["Librería"]),
            ("Cuaderno universitario", "Hojas rayadas, tapa dura.", "4900.00", None, ["Librería"]),
        ],
    },
    {
        "number": 21,
        "name": "Café del Fondo",
        "description": "Café de especialidad, pastelería y bebidas frías.",
        "color": "78350f",
        "hours": "cafe",
        "products": [
            ("Cappuccino", "Espresso, leche y espuma cremosa.", "3800.00", None, ["Gastronomía"]),
            ("Cheesecake", "Base de galleta y frutos rojos.", "6500.00", "5500.00", ["Gastronomía"]),
            ("Té helado", "Infusión de frutos del bosque.", "3200.00", None, ["Gastronomía"]),
        ],
    },
]

# --- Deterministic extra catalog -------------------------------------------
#
# Every store keeps its three curated products and receives 17 extra products
# generated from its commercial categories. Each category defines five base
# products and six variants (30 candidates). The selection is deterministic so
# repeated runs upsert the same names instead of creating new ones.

EXTRAS_PER_STORE = 17
OFFER_EVERY = 3  # one extra out of three gets an offer price
OFFER_FACTOR = Decimal("0.85")
VARIANT_PRICE_FACTORS = (
    Decimal("1.00"),
    Decimal("1.08"),
    Decimal("1.04"),
    Decimal("0.94"),
    Decimal("1.15"),
    Decimal("1.22"),
)

# (base name, description, base price)
BaseProduct = tuple[str, str, str]

CATEGORY_BASES: dict[str, tuple[BaseProduct, ...]] = {
    "Indumentaria": (
        ("Remera algodón", "Algodón peinado, corte regular.", "14500.00"),
        ("Buzo canguro", "Frisa liviana con capucha.", "27900.00"),
        ("Pantalón jogger", "Elástico en cintura y puños.", "24900.00"),
        ("Camisa de lino", "Tela liviana y calce holgado.", "31900.00"),
        ("Campera liviana", "Cierre frontal y bolsillos laterales.", "45900.00"),
    ),
    "Calzado": (
        ("Zapatilla urbana", "Suela de goma y capellada de lona.", "58900.00"),
        ("Zapatilla de running", "Amortiguación media y malla transpirable.", "74900.00"),
        ("Bota de cuero", "Cuero vacuno y suela antideslizante.", "94900.00"),
        ("Sandalia de verano", "Plantilla acolchada y tiras ajustables.", "23900.00"),
        ("Zapatilla de lona", "Corte clásico con cordones.", "42900.00"),
    ),
    "Accesorios": (
        ("Cartera", "Cuero sintético con correa ajustable.", "38900.00"),
        ("Mochila", "Dos compartimentos y espalda acolchada.", "31900.00"),
        ("Cinturón", "Hebilla metálica y tira de cuero.", "17900.00"),
        ("Gorro de punto", "Tejido grueso con puño doble.", "9900.00"),
        ("Reloj", "Malla de acero y esfera simple.", "45900.00"),
    ),
    "Belleza": (
        ("Crema facial", "Hidratación diaria con aloe vera.", "17900.00"),
        ("Sérum facial", "Ácido hialurónico y vitamina C.", "24900.00"),
        ("Labial", "Larga duración con acabado mate.", "8900.00"),
        ("Máscara de pestañas", "Volumen y curva duradera.", "12900.00"),
        ("Perfume", "Fragancia floral con notas cítricas.", "42900.00"),
    ),
    "Tecnología": (
        ("Auriculares Bluetooth", "Cancelación de ruido y batería extendida.", "39900.00"),
        ("Cargador rápido", "Carga USB-C de alta potencia.", "14900.00"),
        ("Parlante portátil", "Resistente al agua y conexión inalámbrica.", "32900.00"),
        ("Mouse inalámbrico", "Sensor óptico y diseño ergonómico.", "17900.00"),
        ("Teclado compacto", "Teclas silenciosas y perfil bajo.", "42900.00"),
    ),
    "Hogar": (
        ("Juego de toallas", "Algodón absorbente de 500 g.", "22900.00"),
        ("Lámpara de mesa", "Base de madera y pantalla de lino.", "31900.00"),
        ("Set de tazas", "Cuatro tazas de cerámica esmaltada.", "14900.00"),
        ("Organizador", "Tres niveles apilables.", "12900.00"),
        ("Almohadón", "Funda removible y relleno siliconado.", "9900.00"),
    ),
    "Deportes": (
        ("Pelota de fútbol", "Costura reforzada y número 5.", "22900.00"),
        ("Mancuerna", "Recubrimiento antideslizante de 5 kg.", "34900.00"),
        ("Botella deportiva", "Un litro, libre de BPA.", "8900.00"),
        ("Banda elástica", "Resistencia progresiva para entrenar.", "7900.00"),
        ("Colchoneta", "Superficie antideslizante y enrollable.", "18900.00"),
    ),
    "Juguetería": (
        ("Peluche", "Tela extra suave de 40 cm.", "17900.00"),
        ("Set de bloques", "120 piezas de construcción.", "29900.00"),
        ("Auto a control remoto", "Tracción 4x4 y batería recargable.", "42900.00"),
        ("Rompecabezas", "500 piezas con piezas grandes.", "14900.00"),
        ("Juego de mesa", "Partidas de 30 a 60 minutos.", "23900.00"),
    ),
    "Librería": (
        ("Novela contemporánea", "Última edición en tapa blanda.", "17900.00"),
        ("Cuaderno rayado", "Hojas de 80 g y tapa dura.", "4900.00"),
        ("Agenda semanal", "Formato A5 con separadores.", "11900.00"),
        ("Libro infantil", "Ilustraciones a color y letra grande.", "13900.00"),
        ("Set de bolígrafos", "Cuatro colores con punta fina.", "5900.00"),
    ),
    "Gastronomía": (
        ("Café de especialidad", "Grano tostado y molienda fresca.", "3200.00"),
        ("Capuchino", "Espresso, leche y espuma cremosa.", "3800.00"),
        ("Sándwich tostado", "Pan ciabatta con relleno del día.", "5200.00"),
        ("Porción de torta", "Bizcochuelo húmedo y ganache.", "4800.00"),
        ("Jugo natural", "Fruta exprimida al momento.", "2900.00"),
    ),
}

CATEGORY_VARIANTS: dict[str, tuple[str, ...]] = {
    "Indumentaria": (
        "en negro",
        "en blanco",
        "en azul",
        "en gris",
        "en beige",
        "en verde oliva",
    ),
    "Calzado": (
        "talle 37",
        "talle 38",
        "talle 39",
        "talle 40",
        "talle 41",
        "talle 42",
    ),
    "Accesorios": (
        "en negro",
        "en marfil",
        "en azul marino",
        "en bordó",
        "en dorado",
        "en plateado",
    ),
    "Belleza": (
        "clásico",
        "intenso",
        "suave",
        "mini",
        "pack x2",
        "edición limitada",
    ),
    "Tecnología": (
        "básico",
        "plus",
        "pro",
        "mini",
        "max",
        "edición gamer",
    ),
    "Hogar": (
        "en natural",
        "en blanco",
        "en gris",
        "en arena",
        "en verde",
        "en terracota",
    ),
    "Deportes": (
        "nivel inicial",
        "nivel intermedio",
        "nivel avanzado",
        "formato compacto",
        "línea pro",
        "línea premium",
    ),
    "Juguetería": (
        "clásico",
        "mini",
        "deluxe",
        "pack x2",
        "coleccionable",
        "edición color",
    ),
    "Librería": (
        "edición básica",
        "edición premium",
        "formato bolsillo",
        "formato A4",
        "pack x2",
        "edición ilustrada",
    ),
    "Gastronomía": (
        "individual",
        "doble",
        "grande",
        "familiar",
        "para llevar",
        "combo",
    ),
}


def _round_price(value: Decimal) -> Decimal:
    """Round a price to the nearest hundred pesos."""
    hundreds = (value / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return hundreds * 100


@lru_cache(maxsize=None)
def _category_candidates(category_name: str) -> tuple[tuple[str, str, str], ...]:
    """Return the 30 deterministic candidates of a category."""
    bases = CATEGORY_BASES.get(category_name)
    variants = CATEGORY_VARIANTS.get(category_name)
    if not bases or not variants:
        return ()

    candidates: list[tuple[str, str, str]] = []
    for base_name, description, base_price in bases:
        price = Decimal(base_price)
        for index, variant in enumerate(variants):
            candidate_price = _round_price(price * VARIANT_PRICE_FACTORS[index])
            candidates.append(
                (
                    f"{base_name} {variant}",
                    f"{description} Variante: {variant}.",
                    f"{candidate_price:.2f}",
                )
            )
    return tuple(candidates)


def _store_category_names(specs: list[ProductSpec]) -> list[str]:
    """Return the distinct categories of the curated products, in order."""
    names: list[str] = []
    for spec in specs:
        for category_name in spec[4]:
            if category_name not in names:
                names.append(category_name)
    return names


def _extras_for_store(
    number: int,
    existing_names: set[str],
    category_names: list[str],
) -> list[ProductSpec]:
    """Build 17 deterministic extra products alternating store categories."""
    catalogs = {
        category: _category_candidates(category)
        for category in category_names
        if _category_candidates(category)
    }
    ordered = list(catalogs)
    if not ordered:
        return []

    # Different stores start at different offsets to avoid identical catalogs.
    cursors = {
        category: ((number - 1) * 7 + index * 11) % len(catalogs[category])
        for index, category in enumerate(ordered)
    }
    used = set(existing_names)
    extras: list[ProductSpec] = []
    pick = 0
    attempts = 0

    while len(extras) < EXTRAS_PER_STORE and attempts < 1000:
        category = ordered[pick % len(ordered)]
        pick += 1
        attempts += 1

        candidates = catalogs[category]
        cursor = cursors[category]
        chosen: tuple[str, str, str] | None = None
        for _ in range(len(candidates)):
            name, description, price = candidates[cursor % len(candidates)]
            cursor += 1
            if name not in used:
                chosen = (name, description, price)
                break
        cursors[category] = cursor
        if chosen is None:
            continue

        name, description, price = chosen
        used.add(name)
        price_value = Decimal(price)
        offer: Decimal | None = None
        if len(extras) % OFFER_EVERY == 1:
            discounted = _round_price(price_value * OFFER_FACTOR)
            if discounted < price_value:
                offer = discounted

        extras.append(
            (
                name,
                description,
                f"{price_value:.2f}",
                f"{offer:.2f}" if offer is not None else None,
                [category],
            )
        )

    return extras


SHOP_HOURS = [
    (0, "10:00", "20:00"),
    (1, "10:00", "20:00"),
    (2, "10:00", "20:00"),
    (3, "10:00", "20:00"),
    (4, "10:00", "20:00"),
    (5, "10:00", "14:00"),
]

CAFE_HOURS = [
    (0, "08:00", "21:00"),
    (1, "08:00", "21:00"),
    (2, "08:00", "21:00"),
    (3, "08:00", "21:00"),
    (4, "08:00", "21:00"),
    (5, "08:00", "21:00"),
    (6, "09:00", "20:00"),
]


def _slug(value: str) -> str:
    """Return a URL-friendly slug for demo assets."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")


def _logo_url(name: str, color: str) -> str:
    return f"https://placehold.co/200x200/{color}/ffffff?text={quote_plus(name)}"


def _image_urls(name: str) -> list[str]:
    slug = _slug(name)
    return [
        f"https://picsum.photos/seed/{slug}-1/800/600",
        f"https://picsum.photos/seed/{slug}-2/800/600",
    ]


def _hours_for(kind: str) -> list[tuple[int, str, str]]:
    return CAFE_HOURS if kind == "cafe" else SHOP_HOURS


def _ensure_merchant(session, store: Store, number: int) -> tuple[User, bool]:
    """Return the demo merchant for a store, creating it when needed."""
    email = f"comercio{number:02d}@galeria.local"
    merchant = session.scalar(select(User).where(User.email == email))
    if merchant is not None:
        return merchant, False

    existing = session.scalar(
        select(User).where(
            User.store_id == store.id,
            User.role == "merchant",
            User.is_active.is_(True),
        )
    )
    if existing is not None:
        return existing, False

    merchant = User(
        email=email,
        full_name=f"Comerciante {store.name}",
        password_hash=hash_password(DEMO_PASSWORD),
        role="merchant",
        is_active=True,
        store_id=store.id,
    )
    session.add(merchant)
    session.flush()
    return merchant, True


def _replace_hours(session, store: Store, kind: str) -> None:
    store.hours.clear()
    session.flush()
    for day, opens, closes in _hours_for(kind):
        store.hours.append(
            StoreHour(
                day_of_week=day,
                opens_at=time.fromisoformat(opens),
                closes_at=time.fromisoformat(closes),
            )
        )


def _replace_links(session, store: Store, slug: str) -> None:
    store.links.clear()
    session.flush()
    store.links.append(
        StoreLink(
            label="Instagram",
            url=f"https://instagram.com/{slug}",
            position=0,
        )
    )
    store.links.append(
        StoreLink(
            label="Sitio web",
            url=f"https://www.example.com/{slug}",
            position=1,
        )
    )


def _upsert_product(
    session,
    store: Store,
    spec: ProductSpec,
    categories: dict[str, Category],
) -> tuple[bool, bool]:
    """Create or update a demo product; return ``(created, updated)``."""
    name, description, price, offer, category_names = spec
    product = session.scalar(
        select(Product).where(Product.store_id == store.id, Product.name == name)
    )
    created = product is None
    if product is None:
        product = Product(store_id=store.id, name=name)
        session.add(product)

    product.description = description
    product.price = Decimal(price)
    product.offer_price = Decimal(offer) if offer else None
    product.is_active = True
    product.deleted_at = None
    product.is_featured = False

    product.product_categories.clear()
    session.flush()
    for category_name in category_names:
        category = categories.get(category_name)
        if category is not None:
            product.product_categories.append(ProductCategory(category=category))

    product.images.clear()
    session.flush()
    for position, url in enumerate(_image_urls(name)):
        product.images.append(
            ProductImage(
                url=url,
                alt_text=name,
                position=position,
                is_primary=position == 0,
            )
        )

    return created, not created


def seed_demo() -> dict[str, int]:
    """Populate the gallery with demo merchants, store data and products."""
    summary = {"merchants": 0, "products": 0, "stores": 0, "updated": 0}

    with SessionLocal() as session:
        categories = {
            category.name: category
            for category in session.scalars(select(Category)).all()
        }
        if not categories:
            raise RuntimeError(
                "No hay categorías. Ejecuta 'python -m scripts.seed_categories' primero."
            )

        for data in STORES:
            number = int(data["number"])
            store = session.scalar(select(Store).where(Store.number == number))
            if store is None:
                raise RuntimeError(
                    f"No existe el local {number}. Ejecuta 'python -m scripts.seed_stores'."
                )

            name = str(data["name"])
            slug = _slug(name)
            store.name = name
            store.description = str(data["description"])
            store.logo_url = _logo_url(name, str(data["color"]))
            store.email = f"{slug}@galeria.local"
            store.phone = f"11 4000-{number:04d}"
            store.whatsapp = f"549114000{number:04d}"
            store.is_active = True

            _replace_hours(session, store, str(data["hours"]))
            _replace_links(session, store, slug)

            _, created = _ensure_merchant(session, store, number)
            if created:
                summary["merchants"] += 1

            for product_spec in data["products"]:
                created, updated = _upsert_product(
                    session, store, product_spec, categories
                )
                if created:
                    summary["products"] += 1
                if updated:
                    summary["updated"] += 1

            curated_specs = list(data["products"])
            extras = _extras_for_store(
                number,
                {spec[0] for spec in curated_specs},
                _store_category_names(curated_specs),
            )
            for product_spec in extras:
                created, updated = _upsert_product(
                    session, store, product_spec, categories
                )
                if created:
                    summary["products"] += 1
                if updated:
                    summary["updated"] += 1

            summary["stores"] += 1
            session.flush()

        session.commit()

    return summary


def main() -> None:
    summary = seed_demo()
    print(
        "Datos demo generados: "
        f"{summary['stores']} locales, "
        f"{summary['merchants']} comerciantes nuevos, "
        f"{summary['products']} productos nuevos "
        f"({summary['updated']} actualizados)."
    )
    print(f"Contraseña de los comerciantes demo: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
