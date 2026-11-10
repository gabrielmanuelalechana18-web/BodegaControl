from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.bodega_repo import BodegaRepository
from app.models.entities import TransaccionVenta, AbonoDeuda
from app.schemas.dtos import VentaCreate, AbonoCreate, EnvioProveedorCreate
from app.core.config import settings

class BodegaService:
    # Capa de logica de negocio y validacion de Reglas de Negocio (RN01 a RN04) y Transaccionalidad ACID (RNF02)

    @staticmethod
    def procesar_venta(db: Session, payload: VentaCreate):
        prod = BodegaRepository.obtener_producto(db, payload.producto_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no existe en el catalogo.")

        if prod.stock_actual < payload.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{prod.nombre}'. Disponible: {prod.stock_actual}, Solicitado: {payload.cantidad}."
            )

        total_venta = round(prod.precio_venta * payload.cantidad, 2)
        cliente_obj = None

        if payload.es_credito:
            if not payload.cliente_id:
                raise HTTPException(status_code=400, detail="Debe seleccionar un vecino del padron para registrar un fiado (RF04).")
            cliente_obj = BodegaRepository.obtener_cliente(db, payload.cliente_id)
            if not cliente_obj:
                raise HTTPException(status_code=404, detail="Cliente deudor no encontrado en el padron.")

            # RN02: Bloqueo por morosidad > 30 dias
            if cliente_obj.dias_mora > settings.MAX_OVERDUE_DAYS:
                raise HTTPException(
                    status_code=403,
                    detail=f"RN02 Violada: El cliente '{cliente_obj.nombre}' registra {cliente_obj.dias_mora} dias sin abonar (Maximo permitido: {settings.MAX_OVERDUE_DAYS} dias)."
                )

            nuevo_saldo = round(cliente_obj.saldo_deudor + total_venta, 2)
            # RN01: Tope de credito de S/ 100.00 salvo autorizacion de la Sra. Hilda
            if nuevo_saldo > cliente_obj.limite_credito and not payload.autorizacion_duena:
                raise HTTPException(
                    status_code=403,
                    detail=f"RN01 Violada: El nuevo saldo (S/ {nuevo_saldo:.2f}) excede el limite de S/ {cliente_obj.limite_credito:.2f}. Requiere autorizacion de la Sra. Hilda."
                )

            cliente_obj.saldo_deudor = nuevo_saldo

        # Actualizacion transaccional ACID (RNF02)
        prod.stock_actual = round(prod.stock_actual - payload.cantidad, 2)
        nueva_venta = TransaccionVenta(
            producto_id=prod.id,
            producto_nombre=prod.nombre,
            cantidad=payload.cantidad,
            total=total_venta,
            modalidad="CREDITO" if payload.es_credito else "CONTADO",
            cliente_id=cliente_obj.id if cliente_obj else None
        )
        db.add(nueva_venta)
        db.commit()
        db.refresh(prod)

        alerta_critica = prod.stock_actual <= prod.stock_minimo
        return {
            "venta_id": nueva_venta.id,
            "producto": prod.nombre,
            "cantidad": payload.cantidad,
            "total_cobrado": total_venta,
            "modalidad": nueva_venta.modalidad,
            "stock_restante": prod.stock_actual,
            "alerta_stock_critico_RF07": alerta_critica,
            "nuevo_saldo_cliente": cliente_obj.saldo_deudor if cliente_obj else 0.0
        }

    @staticmethod
    def registrar_abono(db: Session, payload: AbonoCreate):
        cliente = BodegaRepository.obtener_cliente(db, payload.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado.")

        if payload.monto > cliente.saldo_deudor:
            raise HTTPException(
                status_code=400,
                detail=f"El abono (S/ {payload.monto:.2f}) no puede superar la deuda actual del vecino (S/ {cliente.saldo_deudor:.2f})."
            )

        cliente.saldo_deudor = round(cliente.saldo_deudor - payload.monto, 2)
        if cliente.saldo_deudor == 0:
            cliente.dias_mora = 0

        abono = AbonoDeuda(cliente_id=cliente.id, monto=payload.monto, medio_pago=payload.medio_pago)
        db.add(abono)
        db.commit()
        return {
            "mensaje": "Abono registrado con exito (RF05)",
            "cliente": cliente.nombre,
            "monto_abonado": payload.monto,
            "nuevo_saldo_deudor": cliente.saldo_deudor
        }

    @staticmethod
    def recepcionar_envio(db: Session, payload: EnvioProveedorCreate):
        prod = BodegaRepository.obtener_producto(db, payload.producto_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        prod.stock_actual = round(prod.stock_actual + payload.cantidad_recibida, 2)
        db.commit()
        return {
            "mensaje": f"Envio de '{payload.proveedor_nombre}' recepcionado (RF06)",
            "producto": prod.nombre,
            "nuevo_stock": prod.stock_actual
        }
