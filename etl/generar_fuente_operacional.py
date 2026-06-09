# -*- coding: utf-8 -*-
"""
Generador de la FUENTE OPERACIONAL sintetica de "Las Salsas de Lucho".
Produce CSVs en data/raw/ que simulan la base transaccional real de la PYME,
incluyendo PROBLEMAS DE CALIDAD DE DATOS intencionales para que el ETL los trate.

Salida (modelo transaccional de origen):
  - categorias.csv
  - productos.csv
  - clientes.csv
  - canales.csv
  - vendedores.csv
  - promociones.csv
  - ventas.csv            (encabezado de factura)
  - detalle_ventas.csv    (linea de factura -> grano del hecho)
  - movimientos_inventario.csv

Reproducible: semilla fija.
"""
import os, csv, random, datetime as dt
import numpy as np

random.seed(42); np.random.seed(42)
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.normpath(os.path.join(HERE, "..", "data", "raw"))
os.makedirs(RAW, exist_ok=True)

def w(name, header, rows):
    p = os.path.join(RAW, name)
    with open(p, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)
    print(f"  {name:32s} {len(rows):6d} filas")

# ---------------------------------------------------------------------------
# 1) CATEGORIAS
# ---------------------------------------------------------------------------
categorias = [
    (1, "Picantes"),
    (2, "Aderezos"),
    (3, "Especialidad Gourmet"),
]
w("categorias.csv", ["id_categoria", "nombre_categoria"], categorias)

# ---------------------------------------------------------------------------
# 2) PRODUCTOS  (3 estrella de alta rotacion + resto de baja rotacion)
#    id, nombre, id_categoria, presentacion_ml, precio_lista, costo_unitario, estrella
# ---------------------------------------------------------------------------
productos = [
    # --- 3 ESTRELLA (alta rotacion) ---
    (101, "Salsa Picante Habanero Lucho", 1, 250, 2200, 760, 1),
    (102, "Chilero Criollo Lucho",        1, 250, 2000, 690, 1),
    (103, "Salsa de Ajo Lucho",           2, 250, 2400, 820, 1),
    # --- BAJA ROTACION (inventadas, venden poco) ---
    (104, "Salsa Mango-Habanero",         3, 250, 3200, 1350, 0),
    (105, "Salsa BBQ Tamarindo",          3, 250, 3000, 1280, 0),
    (106, "Salsa Chipotle Dulce",         1, 250, 2900, 1190, 0),
    (107, "Salsa Verde Jalapeno",         1, 250, 2500, 980,  0),
    (108, "Aderezo Cilantro-Limon",       2, 250, 2600, 1010, 0),
    (109, "Salsa Inferno Carolina Reaper",3, 120, 4500, 2100, 0),
    (110, "Salsa Curry Tropical",         3, 250, 3400, 1520, 0),
]
# se inyecta inconsistencia de mayusculas/espacios en algunos nombres mas adelante (catalogo limpio aqui)
w("productos.csv",
  ["id_producto","nombre_producto","id_categoria","presentacion_ml","precio_lista","costo_unitario","es_estrella"],
  productos)

# ---------------------------------------------------------------------------
# 3) CANALES  (con variantes "sucias" de texto para homologar en ETL)
# ---------------------------------------------------------------------------
canales = [
    (1, "Tienda fisica"),
    (2, "Feria del agricultor"),
    (3, "Mayoreo"),
    (4, "En linea"),
]
w("canales.csv", ["id_canal","nombre_canal"], canales)

# ---------------------------------------------------------------------------
# 4) VENDEDORES
# ---------------------------------------------------------------------------
vendedores = [
    (1, "Luis 'Lucho' Mora",  "Propietario"),
    (2, "Carolina Vargas",    "Ventas"),
    (3, "Diego Soto",         "Ventas"),
    (4, "Maria Jose Rojas",   "Ferias"),
]
w("vendedores.csv", ["id_vendedor","nombre_vendedor","puesto"], vendedores)

# ---------------------------------------------------------------------------
# 5) PROMOCIONES
# ---------------------------------------------------------------------------
promociones = [
    (0, "Sin promocion",        0.00),
    (1, "Descuento mayoreo",    0.12),
    (2, "Combo feria 2x",       0.15),
    (3, "Temporada alta",       0.08),
    (4, "Liquidacion lenta",    0.25),
]
w("promociones.csv", ["id_promocion","nombre_promocion","descuento_pct"], promociones)

# ---------------------------------------------------------------------------
# 6) CLIENTES  (minoristas "contado" + mayoristas con nombre)
#    se inyectan: nulos en fecha_registro, provincias inconsistentes
# ---------------------------------------------------------------------------
provincias_variantes = {
    "San Jose":  ["San Jose", "san jose", "SAN JOSE", "S.J.", " San Jose "],
    "Cartago":   ["Cartago", "cartago", "CARTAGO", " Cartago"],
    "Heredia":   ["Heredia", "heredia", "HEREDIA"],
    "Alajuela":  ["Alajuela", "alajuela", "ALAJUELA"],
    "Guanacaste":["Guanacaste", "guanacaste"],
    "Puntarenas":["Puntarenas", "puntarenas"],
    "Limon":     ["Limon", "limon", "LIMON"],
}
prov_keys = list(provincias_variantes.keys())

clientes = []
# cliente 1 = consumidor final generico ("contado")
clientes.append((1, "Cliente Contado", "Minorista", "San Jose", "", "Walk-in"))
cid = 2
# mayoristas (pulperias / restaurantes / sodas) -> pocos pero concentran ingreso
mayoristas_nombres = [
    "Pulperia La Esquina","Mini Super El Cruce","Soda Doña Tere","Restaurante El Fogon",
    "Super Las Brisas","Abastecedor San Blas","Soda La U","Marisqueria Mar Azul",
    "Pulperia Don Beto","Mini Super Familiar","Restaurante Sabor Tico","Cafeteria Central",
]
for nm in mayoristas_nombres:
    prov = random.choice(prov_keys)
    prov_txt = random.choice(provincias_variantes[prov])
    # fecha_registro entre 2021 y 2025; algunos nulos
    if random.random() < 0.12:
        freg = ""  # NULO intencional
    else:
        start = dt.date(2021,1,1); end = dt.date(2025,6,1)
        freg = (start + dt.timedelta(days=random.randint(0,(end-start).days))).isoformat()
    clientes.append((cid, nm, "Mayorista", prov_txt, freg, "Comercio"))
    cid += 1
# minoristas con nombre (consumidores frecuentes)
nombres_pila = ["Ana","Jose","Luis","Marta","Carlos","Sofia","Diego","Laura","Pedro","Karla",
                "Andres","Gabriela","Mauricio","Daniela","Esteban","Natalia","Rodrigo","Paula"]
apellidos = ["Mora","Jimenez","Rojas","Vargas","Castro","Soto","Chaves","Quiros","Mena","Solano"]
for _ in range(60):
    nm = f"{random.choice(nombres_pila)} {random.choice(apellidos)}"
    prov = random.choice(prov_keys)
    prov_txt = random.choice(provincias_variantes[prov])
    if random.random() < 0.10:
        freg = ""
    else:
        start = dt.date(2023,1,1); end = dt.date(2025,12,1)
        freg = (start + dt.timedelta(days=random.randint(0,(end-start).days))).isoformat()
    clientes.append((cid, nm, "Minorista", prov_txt, freg, "Consumidor"))
    cid += 1
w("clientes.csv",
  ["id_cliente","nombre_cliente","tipo_cliente","provincia","fecha_registro","segmento_origen"],
  clientes)

# ---------------------------------------------------------------------------
# 7) VENTAS + DETALLE  (2 anios de historia, estacionalidad, mix realista)
# ---------------------------------------------------------------------------
canal_variantes = {
    1: ["Tienda fisica","tienda fisica","TIENDA FISICA","Tienda Fisica "," tienda  fisica"],
    2: ["Feria del agricultor","feria","Feria","FERIA DEL AGRICULTOR"],
    3: ["Mayoreo","mayoreo","MAYOREO","Venta mayoreo"],
    4: ["En linea","en linea","EN LINEA","Online","en  linea"],
}
nombre_prod_sucio = {  # variantes de texto para homologar
    101: ["Salsa Picante Habanero Lucho","SALSA PICANTE HABANERO LUCHO","salsa picante habanero lucho "],
    102: ["Chilero Criollo Lucho","chilero criollo lucho","Chilero Criollo  Lucho"],
    103: ["Salsa de Ajo Lucho","SALSA DE AJO LUCHO","salsa de ajo lucho"],
}

prod_ids = [p[0] for p in productos]
precio_lista = {p[0]: p[4] for p in productos}
costo_unit  = {p[0]: p[5] for p in productos}
estrella    = {p[0]: p[6] for p in productos}
# pesos de demanda: estrella alto, resto bajo
peso_prod = {}
for pid in prod_ids:
    peso_prod[pid] = (40 if estrella[pid]==1 else 3)
# ajustar entre las 3 estrella
peso_prod[101] = 50; peso_prod[102] = 42; peso_prod[103] = 38

mayoristas_ids = [c[0] for c in clientes if c[2]=="Mayorista"]
minoristas_ids = [c[0] for c in clientes if c[2]=="Minorista" and c[0]!=1]

ventas_rows = []
detalle_rows = []
venta_id = 1000
linea_global = 1

def estacionalidad(d):
    # temporada alta: nov-dic (fiestas) y jul (vacaciones); feb bajo
    m = d.month
    f = 1.0
    if m in (11,12): f = 1.7
    elif m == 7: f = 1.3
    elif m in (1,2): f = 0.8
    elif m in (4,): f = 1.15   # Semana Santa
    # fines de semana mas ventas (ferias)
    if d.weekday() in (5,6): f *= 1.25
    return f

start = dt.date(2024,1,1); end = dt.date(2025,12,31)
ndays = (end-start).days
for i in range(ndays+1):
    d = start + dt.timedelta(days=i)
    base = 6  # facturas base por dia
    nfact = max(0, int(np.random.poisson(base * estacionalidad(d))))
    for _ in range(nfact):
        venta_id += 1
        # canal
        canal = random.choices([1,2,3,4], weights=[35,25,20,20])[0]
        # cliente segun canal
        if canal == 3:
            cliente = random.choice(mayoristas_ids)
        elif canal == 1:
            cliente = 1 if random.random() < 0.7 else random.choice(minoristas_ids)
        elif canal == 2:
            cliente = 1 if random.random() < 0.85 else random.choice(minoristas_ids)
        else:
            cliente = random.choice(minoristas_ids) if random.random()<0.6 else 1
        vendedor = random.choice([1,2,3,4])
        # promocion
        if canal == 3 and random.random() < 0.5:
            promo = 1
        elif canal == 2 and random.random() < 0.3:
            promo = 2
        elif d.month in (11,12) and random.random() < 0.25:
            promo = 3
        elif random.random() < 0.05:
            promo = 4
        else:
            promo = 0
        # canal texto sucio
        canal_txt = random.choice(canal_variantes[canal])
        fecha_txt = d.isoformat()
        # numero de lineas
        nlineas = random.choices([1,2,3,4], weights=[55,28,12,5])[0]
        prods_en_factura = set()
        total_factura = 0.0
        lineas_buffer = []
        for _l in range(nlineas):
            pid = random.choices(prod_ids, weights=[peso_prod[p] for p in prod_ids])[0]
            if pid in prods_en_factura:
                continue
            prods_en_factura.add(pid)
            # cantidad: mayoreo compra mas
            if canal == 3:
                cant = random.choices([6,12,24,36],weights=[30,40,20,10])[0]
            else:
                cant = random.choices([1,2,3],weights=[70,22,8])[0]
            precio = precio_lista[pid]
            # algo de variacion de precio
            if random.random() < 0.1:
                precio = int(precio * random.choice([0.95,1.05]))
            descp = promociones[promo][2]
            monto_bruto = precio * cant
            descuento = round(monto_bruto * descp, 2)
            # nombre producto: a veces sucio para estrellas
            if pid in nombre_prod_sucio and random.random() < 0.3:
                pnombre = random.choice(nombre_prod_sucio[pid])
            else:
                pnombre = next(p[1] for p in productos if p[0]==pid)
            # costo: a veces nulo (se imputa en ETL)
            costo = costo_unit[pid]
            costo_field = "" if random.random() < 0.04 else costo
            lineas_buffer.append([pid, pnombre, cant, precio, monto_bruto, descuento, costo_field])
            total_factura += (monto_bruto - descuento)

        if not lineas_buffer:
            continue
        ventas_rows.append([venta_id, fecha_txt, cliente, canal, canal_txt, vendedor, promo,
                            round(total_factura,2)])
        for lb in lineas_buffer:
            detalle_rows.append([linea_global, venta_id] + lb)
            linea_global += 1

# ---- INYECCION DE PROBLEMAS DE CALIDAD ----
# a) duplicados exactos de lineas (5%)
ndup = int(len(detalle_rows)*0.005)
for _ in range(ndup):
    src = random.choice(detalle_rows)
    dup = src.copy(); dup[0] = linea_global; linea_global += 1
    detalle_rows.append(dup)
# b) outliers de cantidad (errores de digitacion)
for _ in range(25):
    r = random.choice(detalle_rows)
    r[4] = random.choice([999, 1500, 9999])   # cantidad absurda
# c) cantidades negativas / cero (devoluciones mal registradas)
for _ in range(18):
    r = random.choice(detalle_rows)
    r[4] = random.choice([0, -2, -1])
# d) canal nulo en algunas ventas
for _ in range(40):
    r = random.choice(ventas_rows)
    r[4] = ""   # canal_texto vacio
# e) cliente inexistente (FK rota) en algunas ventas
for _ in range(15):
    r = random.choice(ventas_rows)
    r[2] = 99999  # id_cliente inexistente

w("ventas.csv",
  ["id_venta","fecha_venta","id_cliente","id_canal","canal_texto","id_vendedor","id_promocion","total_factura"],
  ventas_rows)
w("detalle_ventas.csv",
  ["id_linea","id_venta","id_producto","nombre_producto_texto","cantidad","precio_unitario","monto_bruto","descuento","costo_unitario"],
  [[r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8]] for r in
   [[d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8]] for d in detalle_rows]])

# ---------------------------------------------------------------------------
# 8) MOVIMIENTOS DE INVENTARIO (snapshot mensual por producto)
# ---------------------------------------------------------------------------
inv_rows = []
inv_id = 1
# calcular salidas reales por producto/mes desde el detalle
from collections import defaultdict
salidas = defaultdict(int)
for d_ in detalle_rows:
    pid = d_[2]; cant = d_[4]; vid = d_[1]
    # fecha de la venta
    fecha = next((v[1] for v in ventas_rows if v[0]==vid), None)
    if fecha and isinstance(cant,(int,float)) and cant>0 and cant<500:
        ym = fecha[:7]
        salidas[(pid,ym)] += int(cant)

meses = []
y,m = 2024,1
while (y,m) <= (2025,12):
    meses.append(f"{y:04d}-{m:02d}")
    m += 1
    if m>12: m=1; y+=1

existencias = {p[0]: random.randint(120,400) for p in productos}
for pid in prod_ids:
    for ym in meses:
        ini = existencias[pid]
        sal = salidas.get((pid,ym),0)
        # entradas (produccion) buscando mantener stock; estrella produce mas
        objetivo = (sal*1.2) if estrella[pid]==1 else max(20, sal*1.5+30)
        ent = int(max(0, objetivo - (ini - sal)))
        fin = ini + ent - sal
        if fin < 0: fin = 0
        existencias[pid] = fin
        costo_inv = round(fin * costo_unit[pid],2)
        inv_rows.append([inv_id, pid, ym+"-01", ini, ent, sal, fin, costo_inv])
        inv_id += 1
w("movimientos_inventario.csv",
  ["id_mov","id_producto","fecha_corte","existencia_inicial","entradas","salidas","existencia_final","costo_inventario"],
  inv_rows)

print("\nFuente operacional generada en data/raw/")
print(f"Total ventas: {len(ventas_rows)} | lineas: {len(detalle_rows)} | inventario: {len(inv_rows)}")
