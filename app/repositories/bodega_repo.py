from sqlalchemy.orm import Session
from app.models.entities import Producto, Cliente, TransaccionVenta, AbonoDeuda, Usuario

class BodegaRepository:
    # Capa de acceso a datos desacoplada (Principio de Responsabilidad Unica - SOLID)

    @staticmethod
    def listar_productos(db: Session):
        return db.query(Producto).order_by(Producto.id).all()

    @staticmethod
    def obtener_producto(db: Session, prod_id: int):
        return db.query(Producto).filter(Producto.id == prod_id).first()

    @staticmethod
    def crear_producto(db: Session, data: dict):
        prod = Producto(**data)
        db.add(prod)
        db.commit()
        db.refresh(prod)
        return prod

    @staticmethod
    def listar_clientes(db: Session):
        return db.query(Cliente).order_by(Cliente.id).all()

    @staticmethod
    def obtener_cliente(db: Session, cli_id: int):
        return db.query(Cliente).filter(Cliente.id == cli_id).first()

    @staticmethod
    def listar_ventas(db: Session):
        return db.query(TransaccionVenta).order_by(TransaccionVenta.id.desc()).all()

    @staticmethod
    def listar_abonos_cliente(db: Session, cli_id: int):
        return db.query(AbonoDeuda).filter(AbonoDeuda.cliente_id == cli_id).order_by(AbonoDeuda.id.desc()).all()

    @staticmethod
    def autenticar_usuario(db: Session, username: str, password: str):
        return db.query(Usuario).filter(Usuario.username == username, Usuario.password_hash == password).first()
