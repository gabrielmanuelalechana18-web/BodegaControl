from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nombre_completo = Column(String(100), nullable=False)
    rol = Column(String(20), nullable=False)  # DUENA, AYUDANTE, CLIENTE
    password_hash = Column(String(128), nullable=False)
    cliente_id = Column(Integer, nullable=True)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(50), default="Abarrotes")
    costo_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    stock_actual = Column(Float, nullable=False)
    stock_minimo = Column(Float, nullable=False)
    fecha_vencimiento = Column(String(20), nullable=True)

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(150), default="Urb. Vista al Mar")
    telefono = Column(String(20), nullable=True)
    saldo_deudor = Column(Float, default=0.0)
    limite_credito = Column(Float, default=100.0)
    dias_mora = Column(Integer, default=0)

class TransaccionVenta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto_nombre = Column(String(100), nullable=False)
    cantidad = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    modalidad = Column(String(20), nullable=False)  # CONTADO, CREDITO
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    fecha = Column(DateTime, default=utc_now)

class AbonoDeuda(Base):
    __tablename__ = "abonos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    monto = Column(Float, nullable=False)
    medio_pago = Column(String(30), default="Efectivo / Yape")
    fecha = Column(DateTime, default=utc_now)
