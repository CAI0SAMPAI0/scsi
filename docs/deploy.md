# Deploy com Docker Swarm

## Pré-requisitos

- VPS Ubuntu 22.04/24.04
- Docker + Docker Swarm
- Domínio `scsi.digital` no Cloudflare

## Passos

### 1. Preparar o servidor
```bash
ssh root@SEU_IP
apt update && apt upgrade -y
adduser deploy
usermod -aG sudo deploy
```

### 2. Firewall
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. Docker + Swarm
```bash
curl -fsSL https://get.docker.com | sh
docker swarm init --advertise-addr SEU_IP
docker network create --driver overlay --attachable traefik_public
```

### 4. Deploy
```bash
docker build -t ghcr.io/pycodebr/scsi_v1:latest .
docker push ghcr.io/pycodebr/scsi_v1:latest
docker stack deploy -c docker-stack.yml scsi
```

### 5. Migrações
```bash
APP=$(docker ps --filter name=scsi_app -q | head -n1)
docker exec -it $APP python manage.py migrate
docker exec -it $APP python manage.py collectstatic --noinput
docker exec -it $APP python manage.py createsuperuser
```
