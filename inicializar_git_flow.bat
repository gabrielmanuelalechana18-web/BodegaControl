@echo off
git config user.name "Gabriel Manuel Ale Chana"
git config user.email "gabrielmanuelalechana18@gmail.com"

git init
git checkout -b main
git add .gitignore .env.example pytest.ini requirements.txt README.md inicializar_git_flow.sh inicializar_git_flow.bat
git commit -m "chore: initial project structure, pytest config, gitignore and env template"

git checkout -b develop
git add app/__init__.py app/core/ app/models/ app/schemas/
git commit -m "feat(core): configure layered architecture, SQLAlchemy models and Pydantic schemas"

git checkout -b feature/inventario-alertas
git add app/repositories/
git commit -m "feat(inventario): implement repository pattern and stock threshold queries (RF02, RF07)"
git checkout develop
git merge --no-ff feature/inventario-alertas -m "merge: integrate feature/inventario-alertas into develop"

git checkout -b feature/ventas-deudas-rn
git add app/services/ app/controllers/
git commit -m "feat(ventas): add atomic sales, credit limit RN01 and overdue lock RN02 (RF03, RF04, RF05)"
git checkout develop
git merge --no-ff feature/ventas-deudas-rn -m "merge: integrate feature/ventas-deudas-rn into develop"

git checkout -b feature/pwa-mostrador-tests
git add app/static/ app/main.py tests/
git commit -m "feat(ui): build responsive mobile POS interface (<=10s) and unit test suite"
git checkout develop
git merge --no-ff feature/pwa-mostrador-tests -m "merge: integrate feature/pwa-mostrador-tests into develop"

git checkout main
git merge --no-ff develop -m "release: v1.0.0 BodegaControl production ready for Bodega Chanita"

git remote remove origin >nul 2>&1
git remote add origin https://github.com/gabrielmanuelalechana18-web/BodegaControl.git
echo [OK] Las 5 ramas y commits fueron creados y vinculados a https://github.com/gabrielmanuelalechana18-web/BodegaControl.git
