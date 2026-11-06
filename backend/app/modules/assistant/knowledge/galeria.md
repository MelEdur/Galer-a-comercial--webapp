# Guía de la galería comercial

## Qué es la galería

La galería comercial es un espacio con 21 locales organizados en dos lados y un fondo. Reúne locales de rubros variados —indumentaria, calzado, accesorios, belleza, tecnología, hogar, deportes, juguetería, librería y gastronomía— en un mismo lugar.

Esta aplicación web es una guía para visitantes: permite descubrir los locales, explorar sus productos, buscar artículos concretos y ubicar cada local en un mapa esquemático.

La aplicación no procesa compras ni reservas. Tampoco permite modificar datos de los locales desde la vista pública: esa gestión corresponde a cada comerciante desde su panel.

## Cómo usar el buscador

El buscador está disponible en la ruta `/buscar`. Permite escribir el nombre de un producto y combinar filtros por categoría, por rango de precio y por ofertas.

Los resultados muestran el nombre del producto, su precio, su precio de oferta cuando existe, sus categorías y el local que lo vende. Desde un resultado se puede abrir la ficha del producto con toda su información e imágenes.

Si una búsqueda no devuelve resultados, conviene probar con una palabra más general o quitar filtros. También se puede recorrer el catálogo por categorías desde la página de exploración.

## Cómo explorar el catálogo

La ruta `/explorar` reúne una selección de productos destacados, las ofertas vigentes, las categorías comerciales y algunos locales.

Las categorías comerciales son:

- **Indumentaria:** ropa para distintas edades y estilos, como remeras, pantalones, camisas y abrigos.
- **Calzado:** zapatillas, zapatos, botas y sandalias.
- **Accesorios:** carteras, mochilas, cinturones, gorros, joyería y relojes.
- **Belleza:** perfumes, maquillaje, cremas y productos de cuidado personal.
- **Tecnología:** accesorios para dispositivos, audio, informática y pequeños electrodomésticos.
- **Hogar:** artículos de decoración, bazar, cocina y textiles.
- **Deportes:** ropa deportiva, calzado específico y accesorios para actividad física.
- **Juguetería:** juguetes, juegos de mesa y artículos para niños.
- **Librería:** libros, cuadernos, papelería y artículos de escritorio.
- **Gastronomía:** cafeterías, panaderías y locales con comida y bebida para consumir o llevar.

Cada rubro suele ofrecer productos variados; la categoría orienta la búsqueda, pero el detalle exacto de cada artículo aparece en la ficha del producto.

## Cómo ver el detalle de un producto

Cada producto tiene una ficha con su nombre, descripción, precio, precio de oferta si corresponde, imágenes, categorías y el local que lo comercializa.

Desde la ficha se puede consultar el local asociado y volver al buscador para seguir explorando. La disponibilidad y el stock no se muestran en la aplicación.

## Cómo consultar los locales

La ruta `/locales` lista los locales activos con su número, nombre y datos generales. Al abrir un local se muestra su descripción, su información de contacto, sus horarios publicados y sus enlaces externos, además de sus productos disponibles.

Los números de local van del 1 al 21:

- Los números impares del 1 al 19 corresponden al lado derecho, en las posiciones 1 a 10.
- Los números pares del 2 al 20 corresponden al lado izquierdo, en las posiciones 1 a 10.
- El número 21 corresponde al local del fondo, en la posición 1.

El número de local y la posición dentro del lado no son lo mismo. Por ejemplo, el Local 2 está en el lado izquierdo, posición 1, y el Local 3 está en el lado derecho, posición 2. La ficha de cada local y el mapa muestran el lado y la posición reales.

Esa numeración describe la ubicación relativa de cada local dentro de la galería. La aplicación no publica una dirección ni un plano con la entrada, así que no conviene suponer por dónde se ingresa.

## Cómo usar el mapa

La ruta `/mapa` muestra un esquema de la galería con los locales ubicados por lado y posición. Sirve para orientarse y reconocer qué locales están cerca entre sí.

El mapa es esquemático: no incluye coordenadas reales ni indicaciones para llegar desde el exterior. Para consultar los datos de un local conviene abrir su ficha desde la lista de locales o desde el propio mapa.

## Ofertas y precios

La aplicación muestra el precio publicado de cada producto y, cuando existe, un precio de oferta menor. Las ofertas se pueden filtrar desde el buscador y también aparecen destacadas en la página de exploración.

Los precios son informativos y corresponden a lo publicado por cada comerciante. La aplicación no gestiona pagos ni reservas.

## Contacto con los locales

Cada local puede publicar teléfono, WhatsApp, correo electrónico y enlaces a sitios o redes sociales. Esos datos aparecen en la ficha del local.

La aplicación no dispone de un canal de contacto de administración de la galería. La dirección, los horarios generales del edificio y los datos de administración no están publicados en la aplicación.

## Preguntas frecuentes

**¿La aplicación sirve para comprar?** No. Es una guía para descubrir locales y productos; las compras se coordinan directamente con cada local.

**¿Cómo encuentro un producto?** Usa el buscador en `/buscar` o recorre las categorías en `/explorar`.

**¿Cómo sé qué local vende un producto?** La ficha del producto indica el local que lo comercializa.

**¿Puedo ver el stock o la disponibilidad?** No. La aplicación no publica stock ni disponibilidad en tiempo real.

**¿Cómo llego a la galería?** La aplicación no incluye dirección ni indicaciones de acceso. El mapa muestra la ubicación relativa de los locales dentro de la galería.

**¿Los horarios que aparecen son los de la galería?** Los horarios publicados corresponden a cada local. Los horarios generales del edificio no están disponibles en la aplicación.

**¿Cómo contacto a un local?** En la ficha de cada local se muestran los datos de contacto y enlaces que el comerciante haya publicado.

## Alcance del asistente

Este asistente responde consultas informativas sobre la galería, sus locales, sus categorías y el uso de la aplicación.

No busca productos, no consulta precios, no verifica stock y no identifica locales que vendan un artículo específico. Para eso existe el buscador de la aplicación. Tampoco puede modificar datos ni realizar compras o reservas.

Cuando una consulta requiere buscar un producto, el asistente puede ofrecer abrir el buscador. Cuando requiere ubicar un local, puede ofrecer abrir el mapa. En ambos casos la persona decide si quiere continuar.
