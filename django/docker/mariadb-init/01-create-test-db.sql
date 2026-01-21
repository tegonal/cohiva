-- Create main database with correct collation for MariaDB 11.4 compatibility
-- MariaDB 11.4 defaults to utf8mb4_uca1400_ai_ci, but Django/Wagtail expects utf8mb4_unicode_ci
CREATE DATABASE IF NOT EXISTS `cohiva_django_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Create test database for automated tests (also with correct collation)
-- This database is automatically created/destroyed during test runs
CREATE DATABASE IF NOT EXISTS `test_cohiva_django_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `cohiva_gnucash_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `test_cohiva_gnucash_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Grant permissions
GRANT ALL PRIVILEGES ON `cohiva_django_test`.* TO 'cohiva'@'%';
GRANT ALL PRIVILEGES ON `test_cohiva_django_test`.* TO 'cohiva'@'%';
GRANT ALL PRIVILEGES ON `cohiva_gnucash_test`.* TO 'cohiva'@'%';
GRANT ALL PRIVILEGES ON `test_cohiva_gnucash_test`.* TO 'cohiva'@'%';

-- Flush privileges to ensure grants take effect
FLUSH PRIVILEGES;
