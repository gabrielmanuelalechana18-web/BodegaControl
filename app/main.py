from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.entities import Producto, Cliente, Usuario
from app.controllers.api_router import router
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema web movil de gestion de inventarios, ventas en <=10s y control de fiados en Bodega 'Chanita' (Urb. Vista al Mar, Ilo)."
)

app.include_router(router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def inicializar_datos_semilla():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Producto).count() == 0:
            semilla_productos = [
                Producto(nombre="Papel Higiénico Suave x4", categoria="Limpieza", costo_compra=3.50, precio_venta=4.50, stock_actual=12.0, stock_minimo=10.0),
                Producto(nombre="Arroz Costeño x1kg (Granel)", categoria="Abarrotes", costo_compra=3.40, precio_venta=4.20, stock_actual=25.0, stock_minimo=5.0),
                Producto(nombre="Leche Gloria Azul x400g", categoria="Lácteos", costo_compra=3.20, precio_venta=4.00, stock_actual=18.0, stock_minimo=6.0),
                Producto(nombre="Azúcar Rubia x1kg (Granel)", categoria="Abarrotes", costo_compra=3.00, precio_venta=3.80, stock_actual=30.0, stock_minimo=8.0),
                Producto(nombre="Gaseosa Inca Kola 1.5L", categoria="Bebidas", costo_compra=5.20, precio_venta=6.50, stock_actual=8.0, stock_minimo=6.0),
            ]
            db.add_all(semilla_productos)

        if db.query(Cliente).count() == 0:
            semilla_clientes = [
                Cliente(nombre="Juan Pérez (Vecino)", direccion="Mz. C Lt. 4 - Vista al Mar", telefono="953112233", saldo_deudor=30.00, limite_credito=100.00, dias_mora=5),
                Cliente(nombre="María Flores (Docente I.E. Velásquez)", direccion="Frente al Colegio", telefono="953445566", saldo_deudor=0.00, limite_credito=100.00, dias_mora=0),
                Cliente(nombre="Carlos Gómez (Moroso >30d)", direccion="Mz. F Lt. 9 - Vista al Mar", telefono="953998877", saldo_deudor=45.00, limite_credito=100.00, dias_mora=35),
            ]
            db.add_all(semilla_clientes)

        if db.query(Usuario).count() == 0:
            semilla_usuarios = [
                Usuario(username="hilda_admin", nombre_completo="Sra. Hilda (Propietaria)", rol="DUENA", password_hash="Chanita2026*"),
                Usuario(username="operador", nombre_completo="Ayudante Mostrador", rol="AYUDANTE", password_hash="Mostrador2026*"),
                Usuario(username="juan_perez", nombre_completo="Juan Pérez (Vecino)", rol="CLIENTE", password_hash="Vecino123*", cliente_id=1),
            ]
            db.add_all(semilla_usuarios)

        db.commit()
    finally:
        db.close()

inicializar_datos_semilla()

@app.get("/", include_in_schema=False)
def servir_interfaz_pwa():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/health", tags=["Monitoreo y Disponibilidad (RNF03)"])
def health_check():
    return {"status": "ok", "sistema": "BodegaControl", "ubicacion": "Ilo, Moquegua"}
