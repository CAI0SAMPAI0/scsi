# Backup

## Banco de Dados

```bash
# Dump diário
DB=$(docker ps --filter name=scsi_db -q | head -n1)
docker exec $DB pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > /backups/scsi_$(date +%F).sql.gz

# Restore
gunzip -c /backups/scsi_2026-01-01.sql.gz | docker exec -i $DB psql -U $POSTGRES_USER $POSTGRES_DB
```

## Mídia

```bash
# Backup do volume media
docker run --rm -v scsi_media_data:/data -v /backups:/backup alpine tar czf /backup/media_$(date +%F).tar.gz -C /data .
```

## Retenção

- 7 backups diários
- 4 backups semanais
- 12 backups mensais
