# Desenvolvimento Local

## Pré-requisitos

- Python 3.13+
- Docker Compose

## Setup

```bash
# Clone o repositório
git clone https://github.com/pycodebr/scsi.git
cd scsi

# Crie o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Configure o .env
cp .env.example .env
# Edite .env com suas credenciais

# Migrações
python manage.py migrate

# Superusuário
python manage.py createsuperuser

# Execute o servidor
python manage.py runserver
```

## Docker Compose

```bash
docker compose up -d
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser
```

## Seed de Dados

```bash
python manage.py seed_demo
python manage.py seed_demo --flush  # Limpa e recria
```
