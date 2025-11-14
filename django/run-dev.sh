#!/bin/bash

# Configuration
IMAGE_NAME="cohiva-django:dev"
CONTAINER_NAME="cohiva"
MIGRATION_CONTAINER="cohiva-migrate"
DOCKERFILE_PATH="/home/mikel/Documents/cohiva/cohiva/django"

echo "🧹 Cleaning up existing containers and images..."

# Stop and remove existing containers
for container in $CONTAINER_NAME $MIGRATION_CONTAINER; do
    if docker ps -q -f name=$container | grep -q .; then
        echo "Stopping existing container: $container"
        docker stop $container
    fi
    
    if docker ps -aq -f name=$container | grep -q .; then
        echo "Removing existing container: $container"
        docker rm $container
    fi
done

# Remove existing image if it exists
if docker images -q $IMAGE_NAME | grep -q .; then
    echo "Removing existing image: $IMAGE_NAME"
    docker rmi $IMAGE_NAME
fi

echo "🔨 Building new Docker image..."
docker build -t $IMAGE_NAME $DOCKERFILE_PATH

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "🔄 Running database migrations..."

# Step 1: Ensure database exists
echo "Step 1: Creating database if not exists..."
docker run --rm --network host $IMAGE_NAME mysql -h 127.0.0.1 -u cohiva -pc0H1v4 -e "CREATE DATABASE IF NOT EXISTS cohiva_django_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || echo "Database creation skipped (may already exist)"

# Step 1.5: Create user and grant permissions (using root)
echo "Step 1.5: Creating database user and granting permissions..."
docker run --rm --network host $IMAGE_NAME mysql -h 127.0.0.1 -u root -proot -e "
CREATE USER IF NOT EXISTS 'cohiva'@'%' IDENTIFIED BY 'c0H1v4';
CREATE USER IF NOT EXISTS 'cohiva'@'localhost' IDENTIFIED BY 'c0H1v4';
GRANT ALL PRIVILEGES ON cohiva_django_test.* TO 'cohiva'@'%';
GRANT ALL PRIVILEGES ON cohiva_django_test.* TO 'cohiva'@'localhost';
FLUSH PRIVILEGES;
" 2>/dev/null || echo "User creation may have failed - user might already exist"

# Step 2: Run migrations in temporary container
echo "Step 2: Running migrations..."
docker run --rm --network host --name $MIGRATION_CONTAINER $IMAGE_NAME python manage.py migrate --settings=cohiva.settings_docker --noinput --skip-checks

if [ $? -ne 0 ]; then
    echo "❌ Database migration failed!"
    exit 1
fi

echo "✅ Database migrations completed!"

echo "📦 Collecting static files..."
docker run --rm --network host --name cohiva-collectstatic $IMAGE_NAME python manage.py collectstatic --noinput --settings=cohiva.settings_docker

if [ $? -eq 0 ]; then
    echo "✅ Static files collected!"
else
    echo "⚠️  Static files collection failed"
fi

echo "👤 Creating superuser..."
docker run --rm --network host --name cohiva-superuser $IMAGE_NAME python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser \"admin\" created with password \"admin123\"')
else:
    print('Superuser \"admin\" already exists')
"

if [ $? -eq 0 ]; then
    echo "✅ Superuser setup completed!"
else
    echo "⚠️  Superuser creation failed (may already exist)"
fi

echo "🚀 Starting application container..."
docker run -d --name $CONTAINER_NAME --network host $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo "📱 Application available at: http://localhost:8000"
    echo "👤 Login with username: admin, password: admin123"
    echo "📋 View logs: docker logs -f $CONTAINER_NAME"
else
    echo "❌ Failed to start container!"
    exit 1
fi
