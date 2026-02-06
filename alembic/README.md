# KIKI Agent™ Database Migrations

This directory contains Alembic database migrations for the KIKI platform.

## Quick Start

### Apply All Migrations
```bash
# Production
export KIKI_DATABASE_URL="postgresql://user:pass@host:5432/kiki_production"
alembic upgrade head

# Development (SQLite)
alembic upgrade head
```

### Create New Migration
```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add user authentication tables"

# Manual migration
alembic revision -m "Add custom index on campaign_deployments"
```

### Rollback Migration
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### View Migration Status
```bash
# Current database revision
alembic current

# Migration history
alembic history --verbose

# Show pending migrations
alembic show head
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KIKI_DATABASE_URL` | Primary database URL | `sqlite:///./kiki_campaigns.db` |
| `DATABASE_URL` | Fallback database URL | Same as above |

## Migration Workflow

### 1. Development
1. Update models in `/shared/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated migration in `/alembic/versions/`
4. Test migration: `alembic upgrade head`
5. Test rollback: `alembic downgrade -1`
6. Commit migration file to git

### 2. Staging
1. Pull latest code with migrations
2. Backup database: `pg_dump kiki_staging > backup.sql`
3. Apply migrations: `alembic upgrade head`
4. Verify application works
5. If issues, rollback: `alembic downgrade -1`

### 3. Production
1. Schedule maintenance window
2. Backup database: `pg_dump kiki_production > backup_$(date +%Y%m%d).sql`
3. Apply migrations: `alembic upgrade head`
4. Verify application health
5. If issues, rollback immediately: `alembic downgrade -1`

## Best Practices

### ✅ DO
- Review auto-generated migrations before committing
- Test both upgrade and downgrade paths
- Backup database before production migrations
- Use transactions (Alembic default)
- Add data migrations when needed
- Keep migrations atomic and reversible

### ❌ DON'T
- Edit applied migrations (create new ones instead)
- Run migrations without backups in production
- Auto-generate without review (can miss custom logic)
- Delete migration files
- Skip migration testing in development

## Common Tasks

### Add Index
```python
def upgrade():
    op.create_index(
        'idx_campaign_user_id',
        'campaign_deployments',
        ['user_id']
    )

def downgrade():
    op.drop_index('idx_campaign_user_id')
```

### Add Column
```python
def upgrade():
    op.add_column(
        'campaign_deployments',
        sa.Column('archived', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade():
    op.drop_column('campaign_deployments', 'archived')
```

### Data Migration
```python
def upgrade():
    # Update existing rows
    op.execute(
        "UPDATE campaign_deployments SET assets_source = 'GENERATED' "
        "WHERE assets_source IS NULL"
    )

def downgrade():
    # Optional: restore previous state
    pass
```

### Rename Table
```python
def upgrade():
    op.rename_table('old_name', 'new_name')

def downgrade():
    op.rename_table('new_name', 'old_name')
```

## Troubleshooting

### "Target database is not up to date"
```bash
# Check current version
alembic current

# Apply pending migrations
alembic upgrade head
```

### "Can't locate revision identified by X"
```bash
# Stamp database with current code version
alembic stamp head

# Or reset to specific revision
alembic stamp abc123
```

### "Multiple head revisions present"
```bash
# Merge branches
alembic merge heads -m "merge branches"
```

### Manual Stamp (Emergency)
```sql
-- Check current version
SELECT * FROM alembic_version;

-- Manually update (use with caution!)
UPDATE alembic_version SET version_num = 'abc123';
```

## Production Checklist

Before production deployment:

- [ ] Reviewed all migration files
- [ ] Tested upgrade path in development
- [ ] Tested downgrade path (rollback)
- [ ] Backed up production database
- [ ] Scheduled maintenance window
- [ ] Documented any manual steps
- [ ] Prepared rollback plan
- [ ] Verified application compatibility
- [ ] Tested on staging environment
- [ ] Notified team of deployment window

## Support

For issues or questions:
- See `/docs/ARCHITECTURE.md` for database schema details
- Check migration history: `alembic history -v`
- View current state: `alembic current`
- Review Alembic docs: https://alembic.sqlalchemy.org/
