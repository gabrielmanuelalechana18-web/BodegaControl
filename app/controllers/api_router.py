from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.bodega_repo import BodegaRepository
from app.services.bodega_service import BodegaService
from app.schemas.dtos import ProductoCreate, VentaCreate, AbonoCreate, EnvioProveedorCreate, LoginRequest

router = APIRouter(prefix="/api")

@router.post("/auth/login", tags=["M1: Usuarios y Roles (RF01)"])
def iniciar_sesion(cred: LoginRequest, db: Session = Depends(get_db)):
    user = BodegaRepository.autenticar_usuario(db, cred.username, cred.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas.")
    return {
        "username": user.username,
        "nombre_completo": user.nombre_completo,
        "rol": user.rol,
        "cliente_id": user.cliente_id,
        "token_simulado": f"jwt-bodegacontrol-{user.rol.lower()}-token"
    }

@router.get("/productos", tags=["M2: Inventario y Alertas (RF02, RF07)"])
def obtener_catalogo(db: Session = Depends(get_db)):
    productos = BodegaRepository.listar_productos(db)
    resultado = []
    for p in productos:
        alerta = p.stock_actual <= p.stock_minimo
        resultado.append({
            "id": p.id,
            "nombre": p.nombre,
            "categoria": p.categoria,
            "costo_compra": p.costo_compra,
            "precio_venta": p.precio_venta,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "fecha_vencimiento": p.fecha_vencimiento,
            "alerta_stock_critico": alerta
        })
    return resultado

@router.post("/productos", status_code=status.HTTP_201_CREATED, tags=["M2: Inventario y Alertas (RF02, RF07)"])
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    return BodegaRepository.crear_producto(db, payload.model_dump())

@router.post("/ventas", tags=["M3: Ventas Mostrador <=10s (RF03, RF04)"])
def registrar_venta(payload: VentaCreate, db: Session = Depends(get_db)):
    return BodegaService.procesar_venta(db, payload)

@router.get("/clientes", tags=["M4: Deudas y Padron de Vecinos (RF08, RF10)"])
def listar_clientes_deudores(db: Session = Depends(get_db)):
    return BodegaRepository.listar_clientes(db)

@router.get("/clientes/{cliente_id}/estado-cuenta", tags=["M4: Deudas y Padron de Vecinos (RF08, RF10)"])
def consultar_saldo_vecino(cliente_id: int, db: Session = Depends(get_db)):
    cli = BodegaRepository.obtener_cliente(db, cliente_id)
    if not cli:
        raise HTTPException(status_code=404, detail="Vecino no encontrado.")
    abonos = BodegaRepository.listar_abonos_cliente(db, cliente_id)
    return {
        "cliente": cli.nombre,
        "direccion": cli.direccion,
        "saldo_deudor": cli.saldo_deudor,
        "limite_credito": cli.limite_credito,
        "porcentaje_uso": round((cli.saldo_deudor / cli.limite_credito) * 100, 1),
        "dias_mora": cli.dias_mora,
        "historial_abonos": abonos
    }

@router.post("/envios", tags=["M5: Recepcion de Preventistas (RF06)"])
def recepcionar_mercaderia(payload: EnvioProveedorCreate, db: Session = Depends(get_db)):
    return BodegaService.recepcionar_envio(db, payload)

@router.post("/abonos", tags=["M6: Pagos y Amortizaciones (RF05)"])
def registrar_abono(payload: AbonoCreate, db: Session = Depends(get_db)):
    return BodegaService.registrar_abono(db, payload)

@router.get("/reportes/mensual", tags=["M7: Reportes Consolidados (RF09)"])
def obtener_reporte_consolidado(db: Session = Depends(get_db)):
    ventas = BodegaRepository.listar_ventas(db)
    clientes = BodegaRepository.listar_clientes(db)
    productos = BodegaRepository.listar_productos(db)

    total_ventas = round(sum(v.total for v in ventas), 2)
    ventas_contado = round(sum(v.total for v in ventas if v.modalidad == "CONTADO"), 2)
    ventas_credito = round(sum(v.total for v in ventas if v.modalidad == "CREDITO"), 2)
    deuda_total_calle = round(sum(c.saldo_deudor for c in clientes), 2)
    criticos = [p.nombre for p in productos if p.stock_actual <= p.stock_minimo]

    return {
        "negocio": "Bodega 'Chanita' - Sra. Hilda (Urb. Vista al Mar, Ilo)",
        "total_ingresos_brutos": total_ventas,
        "ventas_contado": ventas_contado,
        "ventas_fiadas": ventas_credito,
        "ganancia_estimada_20_pct": round(total_ventas * 0.20, 2),
        "deuda_acumulada_vecinos": deuda_total_calle,
        "productos_en_alerta_critica": criticos,
        "ultimas_transacciones": ventas[:10]
    }
