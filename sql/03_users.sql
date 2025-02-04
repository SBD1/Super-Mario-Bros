\c supermario;

DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dba') THEN
        CREATE USER dba WITH PASSWORD 'senha_dba';
        ALTER USER dba WITH SUPERUSER;
    END IF;
END
$$;

DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'gamer') THEN
        CREATE USER gamer WITH PASSWORD 'senha_gamer';

    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE supermario TO dba;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dba;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dba;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO dba;


GRANT CONNECT ON DATABASE supermario TO gamer;
GRANT USAGE ON SCHEMA public TO gamer;
GRANT SELECT, UPDATE ON ALL TABLES IN SCHEMA public TO gamer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO gamer;


ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, UPDATE ON TABLES TO gamer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO gamer;