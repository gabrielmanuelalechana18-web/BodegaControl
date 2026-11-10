from pydantic import BaseModel, Field, field_validator
from typing import Optional
from app.core.config import settings

class LoginRequest(BaseModel):
    username: str
    password: str

class ProductoCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    categoria: str = Field(default="Abarrotes")
    costo_compra: float = Field(..., gt=0, description="Costo unitario mayor a 0")
    precio_venta: float = Field(..., gt=0, description="Precio de venta al publico")
    stock_actual: float = Field(..., ge=0, description="Admite decimales para venta al peso (arroz/azucar)")
    stock_minimo: float = Field(..., gt=0, description="Umbral para alerta temprana RF07")
    fecha_vencimiento: Optional[str] = "2027-06-30"

    @field_validator("precio_venta")
    @classmethod
    def validar_margen_comercial_rn04(cls, v, info):
        costo = info.data.get("costo_compra")
        if costo is not None:
            minimo_permitido = round(costo * (1.0 + settings.MIN_PROFIT_MARGIN), 2)
            if v < minimo_permitido:
                raise ValueError(
                    f"RN04 Violada: El precio de venta (S/ {v:.2f}) no asegura el margen minimo del "
                    f"{int(settings.MIN_PROFIT_MARGIN * 100)}% sobre el costo (Minimo requerido: S/ {minimo_permitido:.2f})."
                )
        return v

class VentaCreate(BaseModel):
    producto_id: int
    cantidad: float = Field(..., gt=0, description="Cantidad mayor a 0 (soporta fraccionados ej. 0.5 kg)")
    es_credito: bool = False
    cliente_id: Optional[int] = None
    autorizacion_duena: bool = False

class AbonoCreate(BaseModel):
    cliente_id: int
    monto: float = Field(..., gt=0, description="El abono debe ser mayor a S/ 0.00")
    medio_pago: str = Field(default="Efectivo / Yape")

class EnvioProveedorCreate(BaseModel):
    producto_id: int
    cantidad_recibida: float = Field(..., gt=0)
    proveedor_nombre: str = Field(default="Preventista Distribuidora Ilo")
