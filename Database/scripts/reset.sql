SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'dailoqa' AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS dailoqa;
CREATE DATABASE dailoqa;
