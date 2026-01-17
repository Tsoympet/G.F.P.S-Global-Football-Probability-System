# Database Migrations with Alembic

This guide explains how to manage database schema changes using Alembic migrations in the G.F.P.S backend.

## Why Database Migrations?

Database migrations allow you to:
- Version control your database schema
- Apply schema changes consistently across environments
- Roll back changes if needed
- Track the evolution of your database over time

## Setup

Alembic is already configured in the backend. The migration files are located in:
```
backend/
├── alembic/
│   ├── versions/        # Migration files go here
│   ├── env.py          # Alembic environment configuration
│   └── script.py.mako  # Template for new migrations
└── alembic.ini         # Alembic configuration
```

## Basic Usage

### 1. Creating a New Migration

When you make changes to the SQLAlchemy models in `backend/models.py`, generate a migration:

```bash
cd backend
alembic revision --autogenerate -m "Add new column to users table"
```

This creates a new migration file in `alembic/versions/` with auto-detected changes.

**Always review the auto-generated migration** before applying it to ensure it's correct.

### 2. Applying Migrations

To upgrade your database to the latest version:

```bash
cd backend
alembic upgrade head
```

### 3. Checking Current Version

To see which migration version your database is at:

```bash
cd backend
alembic current
```

### 4. Viewing Migration History

To see all available migrations:

```bash
cd backend
alembic history --verbose
```

### 5. Rolling Back Migrations

To downgrade to a previous version:

```bash
cd backend
alembic downgrade -1        # Downgrade one step
alembic downgrade <revision> # Downgrade to specific revision
```

### 6. Manual Migrations

If autogenerate doesn't detect your changes, create an empty migration:

```bash
cd backend
alembic revision -m "Custom migration description"
```

Then edit the generated file in `alembic/versions/` to add your custom SQL.

## Environment Configuration

The database URL is read from the `DATABASE_URL` environment variable. If not set, it falls back to the URL in `alembic.ini`.

```bash
# Development
export DATABASE_URL="sqlite:///./gfps.db"

# Production
export DATABASE_URL="postgresql://user:password@host:5432/gfps"
```

## Migration Best Practices

### DO:
✅ **Review auto-generated migrations** - Alembic may not detect all changes correctly
✅ **Test migrations** on a copy of production data before deploying
✅ **Include both upgrade and downgrade** - Always provide a way to roll back
✅ **Keep migrations small** - One logical change per migration
✅ **Add indexes for foreign keys** - Improves query performance
✅ **Use batch operations for SQLite** - Required for ALTER TABLE operations
✅ **Commit migrations to version control** - Track schema changes over time

### DON'T:
❌ **Don't edit applied migrations** - Create a new migration instead
❌ **Don't delete migration files** - They're part of your schema history
❌ **Don't skip migrations** - Apply them in order
❌ **Don't use raw SQL** unless necessary - Use Alembic operations when possible
❌ **Don't forget data migrations** - Handle existing data when changing schemas

## Common Migration Examples

### Adding a Column

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

### Creating an Index

```python
def upgrade() -> None:
    op.create_index('ix_users_email', 'users', ['email'])

def downgrade() -> None:
    op.drop_index('ix_users_email', 'users')
```

### Renaming a Column

```python
def upgrade() -> None:
    op.alter_column('users', 'user_name', new_column_name='username')

def downgrade() -> None:
    op.alter_column('users', 'username', new_column_name='user_name')
```

### Adding a Foreign Key

```python
def upgrade() -> None:
    op.add_column('coupons', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_coupons_user_id', 'coupons', 'users', ['user_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_coupons_user_id', 'coupons', type_='foreignkey')
    op.drop_column('coupons', 'user_id')
```

### Data Migration

```python
from alembic import op
from sqlalchemy import text

def upgrade() -> None:
    # Add new column
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), default=False))
    
    # Migrate existing data
    conn = op.get_bind()
    conn.execute(text("UPDATE users SET is_premium = FALSE WHERE is_premium IS NULL"))
    
    # Make column non-nullable
    op.alter_column('users', 'is_premium', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'is_premium')
```

## SQLite Considerations

SQLite has limited ALTER TABLE support. For complex changes, use batch operations:

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('new_field', sa.String(50)))
        batch_op.drop_column('old_field')
```

## Production Deployment

Before deploying migrations to production:

1. **Backup your database** - Always have a recovery point
2. **Test on staging** - Verify migrations work on a production-like environment
3. **Check for long-running operations** - Large tables may lock during migration
4. **Plan for downtime** - Some migrations require brief downtime
5. **Monitor after deployment** - Watch for errors or performance issues

### Zero-Downtime Migrations

For large production systems:

1. **Add new columns as nullable** - Make them NOT NULL in a later migration
2. **Use multi-phase migrations** - Deploy code before/after schema changes
3. **Create indexes concurrently** - Use PostgreSQL's CONCURRENTLY option
4. **Avoid dropping columns immediately** - Mark as deprecated first

## Troubleshooting

### Migration Conflicts

If multiple developers create migrations simultaneously:

```bash
# Merge migrations using Alembic
alembic merge -m "merge heads" <revision1> <revision2>
```

### Corrupted Migration State

If Alembic gets confused about the current state:

```bash
# Stamp database with current version
alembic stamp head
```

### Failed Migration

If a migration fails partway through:

```bash
# Check current state
alembic current

# If needed, manually fix the database and stamp the version
alembic stamp <target_revision>
```

## Integration with CI/CD

Add migration checks to your CI pipeline:

```yaml
# In .github/workflows/backend-tests.yml
- name: Check for pending migrations
  run: |
    cd backend
    alembic upgrade head
    alembic check  # Ensures no pending autogenerated changes
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Core Tutorial](https://docs.sqlalchemy.org/en/14/core/tutorial.html)
- [Database Migration Best Practices](https://www.prisma.io/dataguide/types/relational/migration-strategies)

## Version History

- **v1.0** (2026-01-17): Initial database migration documentation
  - Alembic setup and configuration
  - Common migration patterns
  - Best practices and troubleshooting
