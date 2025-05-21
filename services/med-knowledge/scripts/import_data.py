#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Med Knowledge Service数据导入脚本
用于将JSON数据文件导入Neo4j数据库，构建知识图谱
"""

import os
import sys
import json
import logging
from datetime import datetime
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

import neo4j
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("data-import")

# 加载环境变量
load_dotenv()

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"

# Neo4j配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class Neo4jImporter:
    """Neo4j数据导入工具"""

    def __init__(self, uri: str, user: str, password: str):
        """初始化Neo4j连接"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._check_connection()
        
    def _check_connection(self) -> None:
        """检查数据库连接"""
        try:
            self.driver.verify_connectivity()
            logger.info("成功连接到Neo4j数据库")
        except Exception as e:
            logger.error(f"连接Neo4j数据库失败: {str(e)}")
            sys.exit(1)
            
    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self, "driver"):
            self.driver.close()
            logger.info("已关闭Neo4j数据库连接")
            
    def clear_database(self) -> None:
        """清空数据库"""
        with self.driver.session() as session:
            logger.info("清空数据库...")
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("数据库已清空")
            
    def create_indexes(self) -> None:
        """创建索引"""
        with self.driver.session() as session:
            logger.info("创建索引...")
            
            # 为每种节点类型创建索引
            for node_type in ["Constitution", "Symptom", "Acupoint", "Herb", 
                              "Syndrome", "Biomarker", "WesternDisease", 
                              "PreventionEvidence", "IntegratedTreatment", 
                              "LifestyleIntervention"]:
                try:
                    # 为id属性创建唯一约束
                    session.run(f"CREATE CONSTRAINT {node_type.lower()}_id IF NOT EXISTS "
                               f"FOR (n:{node_type}) REQUIRE n.id IS UNIQUE")
                    
                    # 为name属性创建索引
                    session.run(f"CREATE INDEX {node_type.lower()}_name IF NOT EXISTS "
                               f"FOR (n:{node_type}) ON (n.name)")
                except Exception as e:
                    logger.warning(f"创建索引 {node_type} 时出错: {str(e)}")
                    
            logger.info("索引创建完成")
            
    def import_constitutions(self, file_path: Path) -> None:
        """导入体质数据"""
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return
            
        logger.info(f"导入体质数据: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            with self.driver.session() as session:
                for item in data:
                    # 创建体质节点
                    item["created_at"] = datetime.now().isoformat()
                    item["updated_at"] = item["created_at"]
                    
                    session.run(
                        """
                        MERGE (c:Constitution {id: $id})
                        ON CREATE SET 
                            c.name = $name,
                            c.description = $description,
                            c.characteristics = $characteristics,
                            c.symptoms = $symptoms,
                            c.preventions = $preventions,
                            c.food_recommendations = $food_recommendations,
                            c.food_avoidances = $food_avoidances,
                            c.prevalence = $prevalence,
                            c.biomarker_correlations = $biomarker_correlations,
                            c.western_medicine_correlations = $western_medicine_correlations,
                            c.created_at = $created_at,
                            c.updated_at = $updated_at
                        """,
                        item
                    )
                    
            logger.info(f"已导入 {len(data)} 条体质数据")
        except Exception as e:
            logger.error(f"导入体质数据错误: {str(e)}")
            
    def import_syndromes(self, file_path: Path) -> None:
        """导入证型数据"""
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return
            
        logger.info(f"导入证型数据: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            with self.driver.session() as session:
                for item in data:
                    # 创建证型节点
                    item["created_at"] = datetime.now().isoformat()
                    item["updated_at"] = item["created_at"]
                    
                    session.run(
                        """
                        MERGE (s:Syndrome {id: $id})
                        ON CREATE SET 
                            s.name = $name,
                            s.description = $description,
                            s.key_symptoms = $key_symptoms,
                            s.tongue_features = $tongue_features,
                            s.pulse_features = $pulse_features,
                            s.western_correlations = $western_correlations,
                            s.biomarker_patterns = $biomarker_patterns,
                            s.created_at = $created_at,
                            s.updated_at = $updated_at
                        """,
                        item
                    )
                    
                    # 创建与相关症状的关系
                    for symptom in item.get("key_symptoms", []):
                        session.run(
                            """
                            MERGE (sym:Symptom {name: $symptom})
                            ON CREATE SET 
                                sym.id = 'symptom-' + apoc.create.uuid(),
                                sym.description = $symptom,
                                sym.created_at = $created_at
                            WITH sym
                            MATCH (s:Syndrome {id: $syndrome_id})
                            MERGE (s)-[:HAS_SYMPTOM]->(sym)
                            """,
                            {"symptom": symptom, "syndrome_id": item["id"], 
                             "created_at": item["created_at"]}
                        )
                    
                    # 创建与西医疾病的关系
                    for disease in item.get("western_correlations", []):
                        session.run(
                            """
                            MERGE (d:WesternDisease {name: $disease})
                            ON CREATE SET 
                                d.id = 'disease-' + apoc.create.uuid(),
                                d.description = $disease,
                                d.created_at = $created_at
                            WITH d
                            MATCH (s:Syndrome {id: $syndrome_id})
                            MERGE (s)-[:CORRELATES_WITH]->(d)
                            """,
                            {"disease": disease, "syndrome_id": item["id"], 
                             "created_at": item["created_at"]}
                        )
                    
            logger.info(f"已导入 {len(data)} 条证型数据")
        except Exception as e:
            logger.error(f"导入证型数据错误: {str(e)}")
    
    def import_biomarkers(self, file_path: Path) -> None:
        """导入生物标志物数据"""
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return
            
        logger.info(f"导入生物标志物数据: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            with self.driver.session() as session:
                for item in data:
                    # 创建生物标志物节点
                    item["created_at"] = datetime.now().isoformat()
                    item["updated_at"] = item["created_at"]
                    item["intervention_thresholds_json"] = json.dumps(item.get("intervention_thresholds", {}))
                    
                    session.run(
                        """
                        MERGE (b:Biomarker {id: $id})
                        ON CREATE SET 
                            b.name = $name,
                            b.category = $category,
                            b.description = $description,
                            b.normal_range = $normal_range,
                            b.significance = $significance,
                            b.related_diseases = $related_diseases,
                            b.related_syndromes = $related_syndromes,
                            b.related_constitutions = $related_constitutions,
                            b.monitoring_frequency = $monitoring_frequency,
                            b.intervention_thresholds_json = $intervention_thresholds_json,
                            b.created_at = $created_at,
                            b.updated_at = $updated_at
                        """,
                        item
                    )
                    
                    # 创建与相关证型的关系
                    for syndrome_name in item.get("related_syndromes", []):
                        session.run(
                            """
                            MATCH (b:Biomarker {id: $biomarker_id})
                            MATCH (s:Syndrome)
                            WHERE s.name = $syndrome_name OR $syndrome_name IN s.name
                            MERGE (b)-[:INDICATES]->(s)
                            """,
                            {"biomarker_id": item["id"], "syndrome_name": syndrome_name}
                        )
                    
                    # 创建与相关体质的关系
                    for constitution_name in item.get("related_constitutions", []):
                        session.run(
                            """
                            MATCH (b:Biomarker {id: $biomarker_id})
                            MATCH (c:Constitution)
                            WHERE c.name = $constitution_name OR $constitution_name IN c.name
                            MERGE (b)-[:ASSOCIATED_WITH]->(c)
                            """,
                            {"biomarker_id": item["id"], "constitution_name": constitution_name}
                        )
                    
                    # 创建与相关疾病的关系
                    for disease_name in item.get("related_diseases", []):
                        session.run(
                            """
                            MERGE (d:WesternDisease {name: $disease_name})
                            ON CREATE SET 
                                d.id = 'disease-' + apoc.create.uuid(),
                                d.description = $disease_name,
                                d.created_at = $created_at
                            WITH d
                            MATCH (b:Biomarker {id: $biomarker_id})
                            MERGE (b)-[:RELATED_TO]->(d)
                            """,
                            {"disease_name": disease_name, "biomarker_id": item["id"], 
                             "created_at": item["created_at"]}
                        )
                    
            logger.info(f"已导入 {len(data)} 条生物标志物数据")
        except Exception as e:
            logger.error(f"导入生物标志物数据错误: {str(e)}")
    
    def create_relationships(self) -> None:
        """创建实体间的关系"""
        logger.info("创建实体间关系...")
        
        with self.driver.session() as session:
            # 体质与证型的关系
            session.run(
                """
                MATCH (c:Constitution), (s:Syndrome)
                WHERE any(symptom IN s.key_symptoms WHERE 
                      symptom IN c.symptoms OR
                      any(c_symptom IN c.symptoms WHERE c_symptom CONTAINS symptom))
                MERGE (c)-[:TENDS_TO_DEVELOP]->(s)
                """
            )
            logger.info("已创建体质-证型关系")
            
            # 体质与生物标志物的双向关系
            session.run(
                """
                MATCH (c:Constitution), (b:Biomarker)
                WHERE c.name IN b.related_constitutions
                MERGE (c)-[:HAS_BIOMARKER]->(b)
                MERGE (b)-[:INDICATES]->(c)
                """
            )
            logger.info("已创建体质-生物标志物关系")
            
            # 证型与西医疾病的双向关系
            session.run(
                """
                MATCH (s:Syndrome), (d:WesternDisease)
                WHERE s.name IN d.tcm_correlations OR
                      any(corr IN s.western_correlations WHERE d.name CONTAINS corr OR corr CONTAINS d.name)
                MERGE (s)-[:CORRELATES_WITH]->(d)
                MERGE (d)-[:MANIFESTS_AS]->(s)
                """
            )
            logger.info("已创建证型-西医疾病关系")
        
        logger.info("实体间关系创建完成")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Med Knowledge Service数据导入工具")
    parser.add_argument("-c", "--clear", action="store_true", help="清空数据库")
    parser.add_argument("-i", "--indexes", action="store_true", help="创建索引")
    parser.add_argument("-a", "--all", action="store_true", help="导入所有数据")
    parser.add_argument("--constitutions", action="store_true", help="导入体质数据")
    parser.add_argument("--syndromes", action="store_true", help="导入证型数据")
    parser.add_argument("--biomarkers", action="store_true", help="导入生物标志物数据")
    parser.add_argument("--relationships", action="store_true", help="创建实体间关系")
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 创建导入工具
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    
    try:
        # 根据参数执行操作
        if args.clear:
            importer.clear_database()
            
        if args.indexes:
            importer.create_indexes()
            
        if args.all or args.constitutions:
            importer.import_constitutions(DATA_DIR / "constitutions.json")
            
        if args.all or args.syndromes:
            importer.import_syndromes(DATA_DIR / "syndromes.json")
            
        if args.all or args.biomarkers:
            importer.import_biomarkers(DATA_DIR / "biomarkers.json")
            
        if args.all or args.relationships:
            importer.create_relationships()
        
        # 如果没有指定任何操作，则默认导入全部数据
        if not any([args.clear, args.indexes, args.all, 
                   args.constitutions, args.syndromes, 
                   args.biomarkers, args.relationships]):
            logger.info("未指定操作，默认导入全部数据")
            importer.create_indexes()
            importer.import_constitutions(DATA_DIR / "constitutions.json")
            importer.import_syndromes(DATA_DIR / "syndromes.json")
            importer.import_biomarkers(DATA_DIR / "biomarkers.json")
            importer.create_relationships()
            
    finally:
        importer.close()
        
    logger.info("数据导入完成")


if __name__ == "__main__":
    main() 