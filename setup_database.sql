-- Script SQL pour configurer la base de données PostgreSQL
-- Exécuter dans pgAdmin ou psql

-- Créer la base de données
CREATE DATABASE "Trimedh_BD"
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Créer l'utilisateur
CREATE USER admin_Trimedh WITH PASSWORD 'root';

-- Donner les permissions
GRANT ALL PRIVILEGES ON DATABASE "Trimedh_BD" TO admin_Trimedh;
ALTER USER admin_Trimedh CREATEDB;