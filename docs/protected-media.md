# Mídia Protegida

## Princípio

Arquivos **nunca** são servidos publicamente. Todo acesso passa por view autenticada.

## Armazenamento

```
media/
└── brokerage_<id>/
    ├── clients/<uuid>_<filename>
    ├── proposals/<uuid>_<filename>
    ├── policies/<uuid>_<filename>
    └── claims/<uuid>_<filename>
```

## Fluxo de Download

1. Usuário clica em baixar
2. `ProtectedDocumentDownloadView` verifica autenticação
3. Verifica que documento pertence ao tenant
4. Retorna `FileResponse` com `Content-Disposition`
