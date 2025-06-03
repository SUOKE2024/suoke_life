#!/usr/bin/env python3
"""
医学知识数据导入脚本
支持从JSON、CSV、Excel等格式导入数据到Neo4j知识图谱
"""
import asyncio
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from neo4j import AsyncGraphDatabase
import yaml

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.logger import get_logger
from app.core.exceptions import DataImportException, DatabaseException

class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger()
        self.driver = None
        self.stats = {
            "total_records": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def initialize(self):
        """初始化数据库连接"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.settings.database.uri,
                auth=(self.settings.database.username, self.settings.database.password)
            )
            
            # 测试连接
            async with self.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
            
            self.logger.info("数据库连接成功")
            
        except Exception as e:
            self.logger.error(f"数据库连接失败: {e}")
            raise DatabaseException(f"数据库连接失败: {e}")
    
    async def close(self):
        """关闭数据库连接"""
        if self.driver:
            await self.driver.close()
            self.logger.info("数据库连接已关闭")
    
    async def import_data(
        self, 
        source_path: str, 
        data_type: str,
        source_format: str = "json",
        overwrite: bool = False,
        validate_only: bool = False
    ):
        """导入数据"""
        self.stats["start_time"] = datetime.now()
        
        try:
            # 加载数据
            data = await self._load_data(source_path, source_format)
            self.stats["total_records"] = len(data)
            
            self.logger.info(f"开始导入 {data_type} 数据，共 {len(data)} 条记录")
            
            if validate_only:
                # 仅验证数据格式
                await self._validate_data(data, data_type)
                self.logger.info("数据验证完成，格式正确")
                return
            
            # 清理现有数据（如果需要覆盖）
            if overwrite:
                await self._clear_existing_data(data_type)
            
            # 导入数据
            await self._import_by_type(data, data_type)
            
            self.stats["end_time"] = datetime.now()
            duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
            
            self.logger.info(
                f"数据导入完成 - 总计: {self.stats['total_records']}, "
                f"成功: {self.stats['successful_imports']}, "
                f"失败: {self.stats['failed_imports']}, "
                f"耗时: {duration:.2f}秒"
            )
            
        except Exception as e:
            self.logger.error(f"数据导入失败: {e}")
            raise DataImportException(f"数据导入失败: {e}", source=source_path)
    
    async def _load_data(self, source_path: str, source_format: str) -> List[Dict[str, Any]]:
        """加载数据文件"""
        file_path = Path(source_path)
        
        if not file_path.exists():
            raise DataImportException(f"数据文件不存在: {source_path}")
        
        try:
            if source_format.lower() == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
                    else:
                        return [data]
            
            elif source_format.lower() == "csv":
                df = pd.read_csv(file_path)
                return df.to_dict('records')
            
            elif source_format.lower() in ["xlsx", "excel"]:
                df = pd.read_excel(file_path)
                return df.to_dict('records')
            
            elif source_format.lower() in ["yaml", "yml"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'data' in data:
                        return data['data']
                    elif isinstance(data, list):
                        return data
                    else:
                        return [data]
            
            else:
                raise DataImportException(f"不支持的文件格式: {source_format}")
                
        except Exception as e:
            raise DataImportException(f"加载数据文件失败: {e}", source=source_path)
    
    async def _validate_data(self, data: List[Dict[str, Any]], data_type: str):
        """验证数据格式"""
        if not data:
            raise DataImportException("数据为空")
        
        # 根据数据类型验证必需字段
        required_fields = self._get_required_fields(data_type)
        
        for i, record in enumerate(data):
            for field in required_fields:
                if field not in record:
                    raise DataImportException(
                        f"记录 {i+1} 缺少必需字段: {field}",
                        details={"record_index": i, "missing_field": field}
                    )
    
    def _get_required_fields(self, data_type: str) -> List[str]:
        """获取数据类型的必需字段"""
        field_map = {
            "constitutions": ["id", "name", "description"],
            "symptoms": ["id", "name", "description"],
            "acupoints": ["id", "name", "location", "meridian"],
            "herbs": ["id", "name", "properties", "functions"],
            "syndromes": ["id", "name", "description", "symptoms"],
            "biomarkers": ["id", "name", "type", "normal_range"],
            "western_diseases": ["id", "name", "icd_code", "description"],
            "prevention_evidence": ["id", "intervention", "evidence_level", "description"],
            "integrated_treatments": ["id", "name", "tcm_methods", "western_methods"],
            "lifestyle_interventions": ["id", "name", "category", "description"]
        }
        
        return field_map.get(data_type, ["id", "name"])
    
    async def _clear_existing_data(self, data_type: str):
        """清理现有数据"""
        node_labels = {
            "constitutions": "Constitution",
            "symptoms": "Symptom", 
            "acupoints": "Acupoint",
            "herbs": "Herb",
            "syndromes": "Syndrome",
            "biomarkers": "Biomarker",
            "western_diseases": "WesternDisease",
            "prevention_evidence": "PreventionEvidence",
            "integrated_treatments": "IntegratedTreatment",
            "lifestyle_interventions": "LifestyleIntervention"
        }
        
        label = node_labels.get(data_type)
        if not label:
            raise DataImportException(f"未知的数据类型: {data_type}")
        
        async with self.driver.session() as session:
            query = f"MATCH (n:{label}) DETACH DELETE n"
            await session.run(query)
            self.logger.info(f"已清理现有 {label} 数据")
    
    async def _import_by_type(self, data: List[Dict[str, Any]], data_type: str):
        """根据数据类型导入数据"""
        import_methods = {
            "constitutions": self._import_constitutions,
            "symptoms": self._import_symptoms,
            "acupoints": self._import_acupoints,
            "herbs": self._import_herbs,
            "syndromes": self._import_syndromes,
            "biomarkers": self._import_biomarkers,
            "western_diseases": self._import_western_diseases,
            "prevention_evidence": self._import_prevention_evidence,
            "integrated_treatments": self._import_integrated_treatments,
            "lifestyle_interventions": self._import_lifestyle_interventions
        }
        
        import_method = import_methods.get(data_type)
        if not import_method:
            raise DataImportException(f"不支持的数据类型: {data_type}")
        
        await import_method(data)
    
    async def _import_constitutions(self, data: List[Dict[str, Any]]):
        """导入体质数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (c:Constitution {
                        id: $id,
                        name: $name,
                        description: $description,
                        characteristics: $characteristics,
                        recommendations: $recommendations,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "description": record["description"],
                        "characteristics": record.get("characteristics", []),
                        "recommendations": record.get("recommendations", {})
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入体质记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_symptoms(self, data: List[Dict[str, Any]]):
        """导入症状数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (s:Symptom {
                        id: $id,
                        name: $name,
                        description: $description,
                        severity_levels: $severity_levels,
                        related_organs: $related_organs,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "description": record["description"],
                        "severity_levels": record.get("severity_levels", []),
                        "related_organs": record.get("related_organs", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入症状记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_acupoints(self, data: List[Dict[str, Any]]):
        """导入穴位数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (a:Acupoint {
                        id: $id,
                        name: $name,
                        location: $location,
                        meridian: $meridian,
                        functions: $functions,
                        indications: $indications,
                        needling_method: $needling_method,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "location": record["location"],
                        "meridian": record["meridian"],
                        "functions": record.get("functions", []),
                        "indications": record.get("indications", []),
                        "needling_method": record.get("needling_method", "")
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入穴位记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_herbs(self, data: List[Dict[str, Any]]):
        """导入中药数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (h:Herb {
                        id: $id,
                        name: $name,
                        properties: $properties,
                        functions: $functions,
                        indications: $indications,
                        contraindications: $contraindications,
                        dosage: $dosage,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "properties": record["properties"],
                        "functions": record["functions"],
                        "indications": record.get("indications", []),
                        "contraindications": record.get("contraindications", []),
                        "dosage": record.get("dosage", "")
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入中药记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_syndromes(self, data: List[Dict[str, Any]]):
        """导入证型数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (s:Syndrome {
                        id: $id,
                        name: $name,
                        description: $description,
                        symptoms: $symptoms,
                        tongue_signs: $tongue_signs,
                        pulse_signs: $pulse_signs,
                        treatment_principles: $treatment_principles,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "description": record["description"],
                        "symptoms": record["symptoms"],
                        "tongue_signs": record.get("tongue_signs", []),
                        "pulse_signs": record.get("pulse_signs", []),
                        "treatment_principles": record.get("treatment_principles", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入证型记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_biomarkers(self, data: List[Dict[str, Any]]):
        """导入生物标志物数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (b:Biomarker {
                        id: $id,
                        name: $name,
                        type: $type,
                        normal_range: $normal_range,
                        unit: $unit,
                        clinical_significance: $clinical_significance,
                        related_conditions: $related_conditions,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "type": record["type"],
                        "normal_range": record["normal_range"],
                        "unit": record.get("unit", ""),
                        "clinical_significance": record.get("clinical_significance", ""),
                        "related_conditions": record.get("related_conditions", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入生物标志物记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_western_diseases(self, data: List[Dict[str, Any]]):
        """导入西医疾病数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (w:WesternDisease {
                        id: $id,
                        name: $name,
                        icd_code: $icd_code,
                        description: $description,
                        symptoms: $symptoms,
                        risk_factors: $risk_factors,
                        prevention_methods: $prevention_methods,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "icd_code": record["icd_code"],
                        "description": record["description"],
                        "symptoms": record.get("symptoms", []),
                        "risk_factors": record.get("risk_factors", []),
                        "prevention_methods": record.get("prevention_methods", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入西医疾病记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_prevention_evidence(self, data: List[Dict[str, Any]]):
        """导入预防医学证据数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (p:PreventionEvidence {
                        id: $id,
                        intervention: $intervention,
                        evidence_level: $evidence_level,
                        description: $description,
                        study_type: $study_type,
                        population: $population,
                        outcomes: $outcomes,
                        recommendations: $recommendations,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "intervention": record["intervention"],
                        "evidence_level": record["evidence_level"],
                        "description": record["description"],
                        "study_type": record.get("study_type", ""),
                        "population": record.get("population", ""),
                        "outcomes": record.get("outcomes", []),
                        "recommendations": record.get("recommendations", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入预防医学证据记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_integrated_treatments(self, data: List[Dict[str, Any]]):
        """导入中西医结合治疗数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (i:IntegratedTreatment {
                        id: $id,
                        name: $name,
                        tcm_methods: $tcm_methods,
                        western_methods: $western_methods,
                        target_conditions: $target_conditions,
                        efficacy: $efficacy,
                        safety_profile: $safety_profile,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "tcm_methods": record["tcm_methods"],
                        "western_methods": record["western_methods"],
                        "target_conditions": record.get("target_conditions", []),
                        "efficacy": record.get("efficacy", {}),
                        "safety_profile": record.get("safety_profile", {})
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入中西医结合治疗记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1
    
    async def _import_lifestyle_interventions(self, data: List[Dict[str, Any]]):
        """导入生活方式干预数据"""
        async with self.driver.session() as session:
            for record in data:
                try:
                    query = """
                    CREATE (l:LifestyleIntervention {
                        id: $id,
                        name: $name,
                        category: $category,
                        description: $description,
                        target_population: $target_population,
                        implementation: $implementation,
                        expected_outcomes: $expected_outcomes,
                        created_at: datetime(),
                        updated_at: datetime()
                    })
                    """
                    
                    await session.run(query, {
                        "id": record["id"],
                        "name": record["name"],
                        "category": record["category"],
                        "description": record["description"],
                        "target_population": record.get("target_population", []),
                        "implementation": record.get("implementation", {}),
                        "expected_outcomes": record.get("expected_outcomes", [])
                    })
                    
                    self.stats["successful_imports"] += 1
                    
                except Exception as e:
                    self.logger.error(f"导入生活方式干预记录失败: {record.get('id', 'unknown')} - {e}")
                    self.stats["failed_imports"] += 1

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="医学知识数据导入工具")
    parser.add_argument("--source", "-s", required=True, help="数据源文件路径")
    parser.add_argument("--type", "-t", required=True, 
                       choices=[
                           "constitutions", "symptoms", "acupoints", "herbs", "syndromes",
                           "biomarkers", "western_diseases", "prevention_evidence",
                           "integrated_treatments", "lifestyle_interventions"
                       ],
                       help="数据类型")
    parser.add_argument("--format", "-f", default="json",
                       choices=["json", "csv", "xlsx", "excel", "yaml", "yml"],
                       help="数据格式")
    parser.add_argument("--overwrite", action="store_true", help="覆盖现有数据")
    parser.add_argument("--validate-only", action="store_true", help="仅验证数据格式")
    
    args = parser.parse_args()
    
    importer = DataImporter()
    
    try:
        await importer.initialize()
        await importer.import_data(
            source_path=args.source,
            data_type=args.type,
            source_format=args.format,
            overwrite=args.overwrite,
            validate_only=args.validate_only
        )
        
    except Exception as e:
        print(f"导入失败: {e}")
        sys.exit(1)
    
    finally:
        await importer.close()

if __name__ == "__main__":
    asyncio.run(main()) 