#!/bin/bash
set -e

# 创建多个数据库
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE auth_service;
    CREATE DATABASE user_service;
    CREATE DATABASE health_data;
    CREATE DATABASE blockchain_service;
    CREATE DATABASE rag_service;
    CREATE DATABASE integration_service;
    CREATE DATABASE med_knowledge;
    CREATE DATABASE xiaoai_service;
    CREATE DATABASE xiaoke_service;
    CREATE DATABASE laoke_service;
    CREATE DATABASE soer_service;
    CREATE DATABASE inquiry_service;
    CREATE DATABASE look_service;
    CREATE DATABASE listen_service;
    CREATE DATABASE palpation_service;
    CREATE DATABASE medical_resources;
    CREATE DATABASE suoke_bench;
    CREATE DATABASE accessibility_service;
EOSQL
