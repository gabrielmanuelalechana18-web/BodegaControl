# BodegaControl — Sistema Web Móvil de Inventario, Ventas y Deudas

**Caso de Estudio Real:** Bodega *"Chanita"* (Propietaria: Sra. Hilda)  
**Ubicación:** Urb. Vista al Mar, frente a la I.E. Carlos Alberto Velásquez, Ilo, Moquegua.  
**Autor:** Gabriel Manuel Ale Chana (6to Ciclo — EPISI, Universidad Nacional de Moquegua)  
**Docente:** Dr. Alexander Morales Gonzales  

---

## 1. Descripción y Propósito del Sistema
**BodegaControl** es una aplicación web responsiva (PWA) con arquitectura de **Monolito Modular en 3 Capas**, diseñada específicamente para que una sola persona en mostrador pueda registrar ventas al contado o al fiado en **<= 10 segundos (RNF01)**, previniendo quiebres de stock a mitad de mes (como el papel higiénico) y eliminando las pérdidas por olvido de apuntes en cuaderno físico.

---

## 2. Arquitectura del Código (Cumplimiento Dimensión 1 de Auditoría)
El proyecto respeta estrictamente la separación de responsabilidades (**SOLID, DRY, KISS**) en 3 capas:

```text
BodegaControl/
├── app/
│   ├── core/           # Configuración (.env), conexión SQLAlchemy/Neon DB y constantes
│   ├── models/         # Entidades ORM (Producto, Cliente, TransaccionVenta, AbonoDeuda, Usuario)
│   ├── schemas/        # Validaciones Pydantic y reglas de margen comercial (RN04)
│   ├── repositories/   # Capa de Acceso a Datos (Consultas limpias y aisladas)
│   ├── services/       # Capa de Lógica de Negocio (Transacciones ACID y reglas RN01, RN02, RN03)
│   ├── controllers/    # Controladores API REST documentados con OpenAPI/Swagger
│   └── static/         # Interfaz Web Móvil Responsiva fiel a los Wireframes de la SRS 1
├── tests/              # Suite de 6 pruebas automatizadas (Pytest) de flujos y Corner Cases
├── pytest.ini          # Configuración automática de PYTHONPATH para ejecución directa de pytest
├── .env.example        # Plantilla de variables de entorno sin secretos hardcodeados
├── .gitignore          # Exclusión de archivos sensibles (.env, __pycache__, venv)
├── requirements.txt    # Dependencias reproducibles
└── inicializar_git_flow.bat / .sh # Script de generación de ramas y Conventional Commits
```

---

## 3. Guía de Instalación y Ejecución desde Cero (Setup en 1 Minuto)

### Paso 1: Clonar el repositorio y crear el entorno virtual
```bash
git clone https://github.com/gabrielmanuelalechana18-web/BodegaControl.git
cd BodegaControl
python -m venv venv
# Activar en Windows (CMD):
venv\Scripts\activate
# Activar en Linux/Mac/Git Bash:
source venv/bin/activate
```

### Paso 2: Instalar dependencias y configurar `.env`
```bash
pip install -r requirements.txt
copy .env.example .env
```
*(Nota para el Auditor: Si no configura una cadena remota de Neon PostgreSQL en `.env`, el sistema levanta automáticamente una base de datos transaccional local SQLite con los datos semilla de Bodega "Chanita" para que pueda auditar de inmediato).*

### Paso 3: Ejecutar las Pruebas Automatizadas (Pytest)
```bash
pytest -v
```

### Paso 4: Iniciar la aplicación
```bash
python -m uvicorn app.main:app --reload
```

* **Aplicación Web Móvil (PWA Mostrador):** `http://127.0.0.1:8000`
* **Documentación Interactiva API (Swagger UI):** `http://127.0.0.1:8000/docs`
* **Health Check:** `http://127.0.0.1:8000/health`

---

## 4. Matriz de Trazabilidad Rápida para el Auditor (Casos de Prueba en Vivo)

| Código | Regla / Requisito | Cómo probarlo en la interfaz (`http://127.0.0.1:8000`) o en `/docs` |
| :--- | :--- | :--- |
| **RF03 / RF07** | Venta al contado y alerta de stock crítico | Vender `3` unidades de **Papel Higiénico Suave x4** (Stock inicial: 12, Mínimo: 10). El stock baja a `9` y se activa la etiqueta amarilla de **¡Stock Crítico!**. |
| **RN01 (RF04)** | Límite de fiado máximo de S/ 100.00 | Seleccionar **Arroz Costeño**, poner cantidad `20` (S/ 84.00) y pulsar **Cargar a Crédito** para **Juan Pérez** (quien ya debe S/ 30.00 -> Nuevo saldo S/ 114.00). Sin el check de la Sra. Hilda, el sistema bloquea la venta con `HTTP 403`. |
| **RN02 (RF04)** | Bloqueo por morosidad > 30 días | Intentar registrar cualquier venta fiada a **Carlos Gómez (Moroso >30d)**. El sistema rechaza la operación inmediatamente. |
| **RN04 (RF02)** | Margen comercial bruto mínimo del 20% | En la pestaña **Stock**, intentar crear un producto con Costo `S/ 10.00` y Precio Venta `S/ 11.00` (10%). El validador Pydantic rechaza el registro con `HTTP 422`. |
| **RF01 / RNF04** | Control de acceso por roles y privacidad | En el selector superior derecho, cambiar el rol a **Ayudante** (bloquea la pestaña *Reporte*) o a **Vecino: Juan Pérez** (solo muestra su propia deuda y oculta a los demás vecinos). |
