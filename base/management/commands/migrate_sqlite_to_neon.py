import sqlite3
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.apps import apps


class Command(BaseCommand):
    help = 'Migra dados do SQLite local para o banco Neon (PostgreSQL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sqlite-path',
            default='db.sqlite3',
            help='Caminho para o arquivo SQLite (default: db.sqlite3)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria migrado, sem inserir dados',
        )

    def handle(self, *args, **options):
        sqlite_path = options['sqlite_path']
        dry_run = options['dry_run']

        self.stdout.write(self.style.NOTICE(f'Conectando ao SQLite: {sqlite_path}'))
        
        try:
            sqlite_conn = sqlite3.connect(sqlite_path)
            sqlite_conn.row_factory = sqlite3.Row
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao abrir SQLite: {e}'))
            return

        # Verify Neon connection
        self.stdout.write(self.style.NOTICE('Verificando conexão com Neon...'))
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute('SELECT 1')
                db_name = connections['default'].settings_dict['NAME']
                self.stdout.write(self.style.SUCCESS(f'Conectado ao Neon: {db_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao conectar no Neon: {e}'))
            self.stdout.write(self.style.ERROR('Verifique se DATABASE_URL está correto no .env'))
            sqlite_conn.close()
            return

        # Get all tables from SQLite
        cursor_sqlite = sqlite_conn.cursor()
        cursor_sqlite.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        tables = [row[0] for row in cursor_sqlite.fetchall()]
        
        self.stdout.write(self.style.NOTICE(f'Tabelas encontradas no SQLite: {len(tables)}'))
        for t in tables:
            self.stdout.write(f'  - {t}')

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run: nenhum dado será inserido'))
            sqlite_conn.close()
            return

        # Migrate each table
        self.stdout.write(self.style.NOTICE('\nIniciando migração...'))
        
        # Order matters for foreign keys
        table_order = [
            'django_content_type',
            'auth_permission',
            'auth_group',
            'auth_group_permissions',
            'django_session',
            'django_admin_log',
            'tenants_plan',
            'tenants_brokerage',
            'accounts_user',
            'accounts_user_groups',
            'accounts_user_user_permissions',
            'tenants_subscription',
            'documents_document',
            'django_celery_beat_crontabschedule',
            'django_celery_beat_intervalschedule',
            'django_celery_beat_periodictask',
            'django_celery_beat_periodictasks',
            'django_celery_results_taskresult',
            'django_celery_results_chordcounter',
        ]

        # Add any tables not in the predefined order
        for t in tables:
            if t not in table_order:
                table_order.append(t)

        # Filter to only existing tables
        table_order = [t for t in table_order if t in tables]

        migrated = 0
        errors = 0

        with transaction.atomic():
            for table_name in table_order:
                try:
                    # Get columns from SQLite
                    cursor_sqlite.execute(f'PRAGMA table_info({table_name})')
                    columns_info = cursor_sqlite.fetchall()
                    columns = [col[1] for col in columns_info]
                    
                    # Build type map for boolean conversion
                    # SQLite types: INTEGER, TEXT, REAL, BLOB, BOOLEAN
                    col_type_map = {}
                    for col in columns_info:
                        col_name = col[1]
                        col_type = col[2].upper()
                        col_type_map[col_name] = col_type
                    
                    # Get data from SQLite
                    cursor_sqlite.execute(f'SELECT * FROM {table_name}')
                    rows = cursor_sqlite.fetchall()
                    
                    if not rows:
                        self.stdout.write(f'  {table_name}: 0 rows (skip)')
                        continue

                    # Check if table exists in Neon and get its columns
                    with connections['default'].cursor() as cursor_neon:
                        try:
                            cursor_neon.execute(f'SELECT * FROM "{table_name}" LIMIT 0')
                            neon_columns = [desc[0] for desc in cursor_neon.description]
                        except Exception:
                            self.stdout.write(self.style.WARNING(f'  {table_name}: tabela não existe no Neon (skip)'))
                            continue

                    # Get Neon column types for proper casting
                    neon_col_types = {}
                    with connections['default'].cursor() as cursor_neon:
                        cursor_neon.execute(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}'
                        """)
                        for row in cursor_neon.fetchall():
                            neon_col_types[row[0]] = row[1]

                    # Find common columns
                    common_columns = [c for c in columns if c in neon_columns]
                    
                    if not common_columns:
                        self.stdout.write(self.style.WARNING(f'  {table_name}: sem colunas em comum (skip)'))
                        continue

                    # Clear existing data in Neon table (to avoid conflicts)
                    with connections['default'].cursor() as cursor_neon:
                        cursor_neon.execute(f'DELETE FROM "{table_name}"')

                    # Insert data
                    cols_str = ', '.join(f'"{c}"' for c in common_columns)
                    placeholders = ', '.join(['%s'] * len(common_columns))
                    
                    inserted = 0
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        values = []
                        for col in common_columns:
                            val = row_dict.get(col)
                            neon_type = neon_col_types.get(col, '').lower()
                            
                            # Convert SQLite integer booleans to Python booleans
                            if neon_type == 'boolean' and isinstance(val, int):
                                val = bool(val)
                            # Convert JSON strings for PostgreSQL jsonb columns
                            elif neon_type in ('jsonb', 'json') and val is not None and isinstance(val, str):
                                try:
                                    json.loads(val)
                                    # Keep as string, psycopg2 handles it
                                except json.JSONDecodeError:
                                    pass
                            # Convert empty strings to None for nullable fields
                            elif val == '' and neon_type in ('integer', 'bigint', 'smallint', 'numeric', 'real', 'double precision'):
                                val = None
                            
                            values.append(val)
                        
                        try:
                            with connections['default'].cursor() as cursor_neon:
                                cursor_neon.execute(
                                    f'INSERT INTO "{table_name}" ({cols_str}) VALUES ({placeholders})',
                                    values
                                )
                            inserted += 1
                        except Exception as e:
                            errors += 1
                            if errors <= 10:
                                self.stdout.write(self.style.ERROR(f'  Erro em {table_name}: {e}'))
                            elif errors == 11:
                                self.stdout.write(self.style.ERROR('  ... mais erros omitidos'))

                    self.stdout.write(self.style.SUCCESS(f'  {table_name}: {inserted}/{len(rows)} rows'))
                    migrated += inserted

                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f'  Erro processando {table_name}: {e}'))

        # Reset sequences for PostgreSQL (auto-increment)
        self.stdout.write(self.style.NOTICE('\nResetando sequences do PostgreSQL...'))
        with connections['default'].cursor() as cursor_neon:
            for table_name in table_order:
                try:
                    cursor_neon.execute(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{table_name}' AND column_default LIKE 'nextval%'
                    """)
                    seq_cols = [row[0] for row in cursor_neon.fetchall()]
                    for col in seq_cols:
                        cursor_neon.execute(f"""
                            SELECT setval(pg_get_serial_sequence('"{table_name}"', '{col}'), 
                            COALESCE(MAX("{col}"), 1)) FROM "{table_name}"
                        """)
                except Exception:
                    pass

        sqlite_conn.close()

        self.stdout.write(self.style.SUCCESS(f'\nMigração concluída!'))
        self.stdout.write(self.style.SUCCESS(f'  Total inserido: {migrated} registros'))
        if errors:
            self.stdout.write(self.style.WARNING(f'  Erros: {errors}'))
        
        self.stdout.write(self.style.NOTICE('\nPróximos passos:'))
        self.stdout.write('  1. python manage.py createsuperuser (criar superuser no Neon)')
        self.stdout.write('  2. python manage.py runserver (testar o sistema)')
