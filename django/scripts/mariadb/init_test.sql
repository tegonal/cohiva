
CREATE DATABASE IF NOT EXISTS `cohiva_django_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;


CREATE DATABASE IF NOT EXISTS `cohiva_gnucash_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Permissions in order to allow test database creation and deletion during tests

-- Grant permissions
GRANT ALL PRIVILEGES ON `cohiva_django_test`.* TO 'cohiva'@'%';
GRANT ALL PRIVILEGES ON `cohiva_gnucash_test`.* TO 'cohiva'@'%';

GRANT ALL PRIVILEGES ON *.* TO 'cohiva'@'%' WITH GRANT OPTION;
GRANT SHOW DATABASES ON *.* TO 'cohiva'@'%';
GRANT CREATE TABLESPACE ON *.* TO 'cohiva'@'%';

-- Flush privileges to ensure grants take effect
FLUSH PRIVILEGES;

