-- Create test database for automated tests
-- This database is automatically created/destroyed during test runs
CREATE DATABASE IF NOT EXISTS `test_cohiva_django_test`;
GRANT ALL PRIVILEGES ON `test_cohiva_django_test`.* TO 'cohiva'@'%';

-- Flush privileges to ensure grants take effect
FLUSH PRIVILEGES;
