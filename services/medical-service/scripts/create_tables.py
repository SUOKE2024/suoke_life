#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
import yaml
import psycopg2

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.model.config import Config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQL脚本：创建数据库表
CREATE_TABLES_SQL = """
-- 医疗记录表
CREATE TABLE IF NOT EXISTS medical_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    record_date TIMESTAMP NOT NULL,
    doctor_id VARCHAR(36),
    doctor_name VARCHAR(100),
    institution VARCHAR(255),
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment TEXT,
    notes TEXT,
    attachments JSONB,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_medical_records_user_id ON medical_records(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_record_date ON medical_records(record_date);

-- 诊断结果表
CREATE TABLE IF NOT EXISTS diagnosis_results (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    diagnosis_time TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    tcm_diagnosis JSONB,
    western_diagnosis JSONB,
    integrated_diagnosis TEXT,
    health_advice JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_user_id ON diagnosis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnosis_results_diagnosis_time ON diagnosis_results(diagnosis_time);

-- 治疗方案表
CREATE TABLE IF NOT EXISTS treatment_plans (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    diagnosis_id VARCHAR(36) REFERENCES diagnosis_results(id),
    status VARCHAR(20) NOT NULL,
    tcm_treatment JSONB,
    western_treatment JSONB,
    lifestyle_adjustment JSONB,
    follow_up_plan JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_treatment_plans_user_id ON treatment_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_treatment_plans_diagnosis_id ON treatment_plans(diagnosis_id);

-- 健康风险评估表
CREATE TABLE IF NOT EXISTS health_risk_assessments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    assessment_date TIMESTAMP NOT NULL,
    overall_risk_score INTEGER,
    risk_level VARCHAR(20),
    disease_risks JSONB,
    constitution_risk JSONB,
    prevention_recommendations JSONB,
    lifestyle_recommendations JSONB,
    recommended_screenings JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_health_risk_assessments_user_id ON health_risk_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_health_risk_assessments_assessment_date ON health_risk_assessments(assessment_date);

-- 医疗查询表
CREATE TABLE IF NOT EXISTS medical_queries (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    query_text TEXT NOT NULL,
    answer TEXT,
    sources JSONB,
    is_emergency_advice BOOLEAN DEFAULT FALSE,
    disclaimer TEXT,
    follow_up_questions JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_medical_queries_user_id ON medical_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_queries_created_at ON medical_queries(created_at);
CREATE INDEX IF NOT EXISTS idx_medical_queries_query_text_gin ON medical_queries USING gin(to_tsvector('chinese', query_text));
"""

def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            return Config(**config_data)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

def create_database_if_not_exists(config):
    """创建数据库（如果不存在）"""
    try:
        # 连接到默认数据库来创建目标数据库
        conn = psycopg2.connect(
            host=config.database.host,
            port=config.database.port,
            user=config.database.user,
            password=config.database.password,
            dbname="postgres"  # 连接到默认的postgres数据库
        )
        conn.autocommit = True  # 设置自动提交
        cursor = conn.cursor()
        
        # 检查数据库是否存在
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config.database.dbname}'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database: {config.database.dbname}")
            cursor.execute(f"CREATE DATABASE {config.database.dbname}")
            logger.info(f"Database {config.database.dbname} created successfully")
        else:
            logger.info(f"Database {config.database.dbname} already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        sys.exit(1)

def create_tables(config):
    """创建数据库表"""
    try:
        # 连接到目标数据库
        conn = psycopg2.connect(
            host=config.database.host,
            port=config.database.port,
            user=config.database.user,
            password=config.database.password,
            dbname=config.database.dbname
        )
        conn.autocommit = True  # 设置自动提交
        cursor = conn.cursor()
        
        logger.info("Creating tables...")
        cursor.execute(CREATE_TABLES_SQL)
        logger.info("Tables created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='医疗服务数据库表创建工具')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 创建数据库（如果不存在）
    create_database_if_not_exists(config)
    
    # 创建数据库表
    create_tables(config)
    
    logger.info("Database setup completed successfully")

if __name__ == "__main__":
    main() 