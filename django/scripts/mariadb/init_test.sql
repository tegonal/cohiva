-- Drop databases in case they are left over from a previous test run
DROP DATABASE IF EXISTS `test_cohiva_django_test`;
DROP DATABASE IF EXISTS `cohiva_gnucash_test`;

GRANT ALL PRIVILEGES ON *.* TO 'cohiva'@'%' WITH GRANT OPTION;
GRANT SHOW DATABASES ON *.* TO 'cohiva'@'%';
GRANT CREATE TABLESPACE ON *.* TO 'cohiva'@'%';

-- Flush privileges to ensure grants take effect
FLUSH PRIVILEGES;

-- Load demo GnuCash data required for tests
CREATE DATABASE IF NOT EXISTS `cohiva_gnucash_test`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
