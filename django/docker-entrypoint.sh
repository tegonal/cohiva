#!/bin/bash
set -e

echo "🔄 Initializing Cohiva application..."

# Step 0a: Overlay instance-specific files
echo "Step 0a: Overlaying instance-specific files..."
echo "Debug: COHIVA_INSTANCE_PATH = $COHIVA_INSTANCE_PATH"
echo "Debug: Contents of /instance_files:"
ls -la /instance_files/ || echo "Directory /instance_files does not exist"
echo "Debug: Contents of $COHIVA_INSTANCE_PATH:"
ls -la "$COHIVA_INSTANCE_PATH" || echo "Directory $COHIVA_INSTANCE_PATH does not exist"

if [ -d "$COHIVA_INSTANCE_PATH" ]; then
    echo "Found instance files in $COHIVA_INSTANCE_PATH"

    # Copy instance files over application files if they exist
    find "$COHIVA_INSTANCE_PATH" -type f | while read -r file; do
        # Get relative path from instance root
        rel_path="${file#$COHIVA_INSTANCE_PATH/}"
        dest_path="/cohiva/$rel_path"

        echo "  Processing: $file -> $dest_path"

        # Create destination directory if it doesn't exist
        mkdir -p "$(dirname "$dest_path")"

        # Copy instance file over application file
        cp "$file" "$dest_path"
        echo "  ✅ Overridden: $rel_path"
    done

    echo "File overlay completed!"
else
    echo "No instance files found in $COHIVA_INSTANCE_PATH"
fi
echo ""

# Step 0b: Run setup to create directories and files that are still missing from default templates
echo "Step 0b: Running setup to create missing directories and files..."
python setup.py

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! mysql -h "$DB_HOST" -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
    echo "Waiting for database connection..."
    sleep 2
done

echo "✅ Database is ready!"

# Step 1: Ensure database exists
echo "Step 1: Creating database if not exists..."
mysql -h "$DB_HOST" -u root -p"$DB_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || echo "Database creation skipped (may already exist)"

# Step 1.5: Create user and grant permissions
echo "Step 1.5: Creating database user and granting permissions..."
mysql -h "$DB_HOST" -u root -p"$DB_ROOT_PASSWORD" -e "
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED BY '$DB_PASSWORD';
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
" 2>/dev/null || echo "User creation may have failed - user might already exist"

# Step 2: Run migrations
echo "Step 2: Running migrations..."
python manage.py migrate --settings="$DJANGO_SETTINGS_MODULE" --noinput --skip-checks

if [ $? -ne 0 ]; then
    echo "❌ Database migration failed!"
    exit 1
fi

echo "✅ Database migrations completed!"

# Step 3: Collect static files
echo "Step 3: Collecting static files..."
python manage.py collectstatic --settings="$DJANGO_SETTINGS_MODULE" --noinput

if [ $? -eq 0 ]; then
    echo "✅ Static files collected!"
else
    echo "⚠️  Static files collection failed"
fi

# Step 4: Create superuser if it doesn't exist
echo "Step 4: Creating superuser..."
python manage.py shell --settings="$DJANGO_SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser = True).exists():
    User.objects.create_superuser('$SUPERUSER_USERNAME', '$SUPERUSER_EMAIL', '$SUPERUSER_PASSWORD')
    print('Superuser \"$SUPERUSER_USERNAME\" created with email \"$SUPERUSER_EMAIL\"')
else:
    print('Superuser already exists')
" 2>/dev/null || echo "Superuser creation failed"

echo "🚀 Starting Cohiva application..."

# Execute the main command
exec "$@"
