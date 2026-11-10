import pytest
from fastapi.testclient import TestClient
from app.main import app, inicializar_datos_semilla
from app.core.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def reiniciar_bd_entre_pruebas():
    Base.metadata.drop_all(bind=engine)
    inicializar_datos_semilla()
    yield

def test_1_venta_contado_descuenta_stock_y_activa_alerta_rf03_rf07():
    res = client.post("/api/ventas", json={"producto_id": 1, "cantidad": 3, "es_credito": False})
    assert res.status_code == 200
    data = res.json()
    assert data["stock_restante"] == 9.0
    assert data["alerta_stock_critico_RF07"] is True

def test_2_regla_negocio_rn01_tope_credito_100_soles():
    res = client.post("/api/ventas", json={
        "producto_id": 2, "cantidad": 20, "es_credito": True, "cliente_id": 1, "autorizacion_duena": False
    })
    assert res.status_code == 403
    assert "RN01 Violada" in res.json()["detail"]

def test_3_regla_negocio_rn02_bloqueo_morosidad_30_dias():
    res = client.post("/api/ventas", json={
        "producto_id": 3, "cantidad": 1, "es_credito": True, "cliente_id": 3
    })
    assert res.status_code == 403
    assert "RN02 Violada" in res.json()["detail"]

def test_4_regla_negocio_rn04_margen_minimo_20_porciento():
    res = client.post("/api/productos", json={
        "nombre": "Aceite Vegetal 1L",
        "costo_compra": 10.00,
        "precio_venta": 11.00,
        "stock_actual": 10,
        "stock_minimo": 3
    })
    assert res.status_code == 422
    assert "RN04 Violada" in str(res.json())

def test_5_corner_case_abono_excede_deuda_rf05():
    res = client.post("/api/abonos", json={"cliente_id": 1, "monto": 50.00})
    assert res.status_code == 400
    assert "no puede superar la deuda" in res.json()["detail"]

def test_6_corner_case_venta_granel_decimales():
    res = client.post("/api/ventas", json={"producto_id": 4, "cantidad": 0.5, "es_credito": False})
    assert res.status_code == 200
    assert res.json()["stock_restante"] == 29.5
