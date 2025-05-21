#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from internal.model.health_risk import (
    HealthRiskAssessment, HealthRiskAssessmentRequest,
    DiseaseRisk, ConstitutionRisk, RiskLevel
)

logger = logging.getLogger(__name__)


class HealthRiskRepository:
    """健康风险评估仓库实现"""
    
    def __init__(self, db_config):
        """
        初始化健康风险评估仓库
        
        Args:
            db_config: 数据库配置
        """
        self.db_config = db_config
        self._init_db()
    
    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.user,
            password=self.db_config.password,
            dbname=self.db_config.dbname
        )
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建健康风险评估请求表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS health_risk_requests (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        health_data JSONB,
                        family_history JSONB,
                        lifestyle_factors JSONB,
                        environmental_factors JSONB,
                        include_genetic_analysis BOOLEAN NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_health_risk_requests_user_id ON health_risk_requests(user_id);
                    ''')
                    
                    # 创建健康风险评估结果表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS health_risk_assessments (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        assessment_date TIMESTAMP NOT NULL,
                        overall_risk_score INTEGER NOT NULL,
                        risk_level VARCHAR(20) NOT NULL,
                        disease_risks JSONB,
                        constitution_risk JSONB,
                        prevention_recommendations JSONB,
                        lifestyle_recommendations JSONB,
                        recommended_screenings JSONB,
                        created_at TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_health_risk_assessments_user_id ON health_risk_assessments(user_id);
                    CREATE INDEX IF NOT EXISTS idx_health_risk_assessments_assessment_date ON health_risk_assessments(assessment_date);
                    CREATE INDEX IF NOT EXISTS idx_health_risk_assessments_risk_level ON health_risk_assessments(risk_level);
                    ''')
                conn.commit()
                logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_request(self, request: HealthRiskAssessmentRequest) -> HealthRiskAssessmentRequest:
        """
        保存健康风险评估请求
        
        Args:
            request: 健康风险评估请求
            
        Returns:
            HealthRiskAssessmentRequest: 保存的健康风险评估请求
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO health_risk_requests (
                        id, user_id, health_data, family_history, lifestyle_factors,
                        environmental_factors, include_genetic_analysis, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        request.id, request.user_id, json.dumps(request.health_data),
                        json.dumps(request.family_history), json.dumps(request.lifestyle_factors),
                        json.dumps(request.environmental_factors),
                        request.include_genetic_analysis, request.created_at
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            return request
        except Exception as e:
            logger.error(f"Error saving health risk request: {str(e)}")
            raise
    
    def get_request_by_id(self, request_id: str) -> Optional[HealthRiskAssessmentRequest]:
        """
        通过ID获取健康风险评估请求
        
        Args:
            request_id: 请求ID
            
        Returns:
            Optional[HealthRiskAssessmentRequest]: 健康风险评估请求，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM health_risk_requests WHERE id = %s', (request_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return HealthRiskAssessmentRequest(
                            id=result["id"],
                            user_id=result["user_id"],
                            health_data=result["health_data"],
                            family_history=result["family_history"],
                            lifestyle_factors=result["lifestyle_factors"],
                            environmental_factors=result["environmental_factors"],
                            include_genetic_analysis=result["include_genetic_analysis"],
                            created_at=result["created_at"]
                        )
                    
                    return None
        except Exception as e:
            logger.error(f"Error getting health risk request by ID: {str(e)}")
            raise
    
    def save_assessment(self, assessment: HealthRiskAssessment) -> HealthRiskAssessment:
        """
        保存健康风险评估结果
        
        Args:
            assessment: 健康风险评估结果
            
        Returns:
            HealthRiskAssessment: 保存的健康风险评估结果
        """
        try:
            # 转换疾病风险为JSON
            disease_risks_json = []
            for risk in assessment.disease_risks:
                disease_risks_json.append({
                    "disease_name": risk.disease_name,
                    "risk_score": risk.risk_score,
                    "risk_level": risk.risk_level.value,
                    "risk_factors": risk.risk_factors,
                    "preventive_measures": risk.preventive_measures
                })
            
            # 转换体质风险为JSON
            constitution_risk_json = None
            if assessment.constitution_risk:
                constitution_risk_json = {
                    "constitution_type": assessment.constitution_risk.constitution_type,
                    "imbalances": assessment.constitution_risk.imbalances,
                    "vulnerable_systems": assessment.constitution_risk.vulnerable_systems,
                    "protective_measures": assessment.constitution_risk.protective_measures
                }
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO health_risk_assessments (
                        id, user_id, assessment_date, overall_risk_score, risk_level,
                        disease_risks, constitution_risk, prevention_recommendations,
                        lifestyle_recommendations, recommended_screenings, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        assessment.id, assessment.user_id, assessment.assessment_date,
                        assessment.overall_risk_score, assessment.risk_level.value,
                        json.dumps(disease_risks_json),
                        json.dumps(constitution_risk_json) if constitution_risk_json else None,
                        json.dumps(assessment.prevention_recommendations),
                        json.dumps(assessment.lifestyle_recommendations),
                        json.dumps(assessment.recommended_screenings),
                        assessment.created_at
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            return assessment
        except Exception as e:
            logger.error(f"Error saving health risk assessment: {str(e)}")
            raise
    
    def get_assessment_by_id(self, assessment_id: str) -> Optional[HealthRiskAssessment]:
        """
        通过ID获取健康风险评估结果
        
        Args:
            assessment_id: 评估ID
            
        Returns:
            Optional[HealthRiskAssessment]: 健康风险评估结果，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM health_risk_assessments WHERE id = %s', (assessment_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
                    
                    # 解析风险等级
                    risk_level = RiskLevel(result["risk_level"])
                    
                    # 解析疾病风险
                    disease_risks = []
                    if result["disease_risks"]:
                        for risk_json in result["disease_risks"]:
                            disease_risks.append(DiseaseRisk(
                                disease_name=risk_json["disease_name"],
                                risk_score=risk_json["risk_score"],
                                risk_level=RiskLevel(risk_json["risk_level"]),
                                risk_factors=risk_json["risk_factors"],
                                preventive_measures=risk_json["preventive_measures"]
                            ))
                    
                    # 解析体质风险
                    constitution_risk = None
                    if result["constitution_risk"]:
                        constitution_json = result["constitution_risk"]
                        constitution_risk = ConstitutionRisk(
                            constitution_type=constitution_json["constitution_type"],
                            imbalances=constitution_json["imbalances"],
                            vulnerable_systems=constitution_json["vulnerable_systems"],
                            protective_measures=constitution_json["protective_measures"]
                        )
                    
                    # 创建健康风险评估
                    assessment = HealthRiskAssessment(
                        id=result["id"],
                        user_id=result["user_id"],
                        assessment_date=result["assessment_date"],
                        overall_risk_score=result["overall_risk_score"],
                        risk_level=risk_level,
                        disease_risks=disease_risks,
                        constitution_risk=constitution_risk,
                        prevention_recommendations=result["prevention_recommendations"],
                        lifestyle_recommendations=result["lifestyle_recommendations"],
                        recommended_screenings=result["recommended_screenings"],
                        created_at=result["created_at"]
                    )
                    
                    return assessment
        except Exception as e:
            logger.error(f"Error getting health risk assessment by ID: {str(e)}")
            raise
    
    def list_assessments(self, filters: Dict[str, Any], page: int = 1, page_size: int = 10) -> Tuple[List[HealthRiskAssessment], int]:
        """
        列出健康风险评估结果
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[HealthRiskAssessment], int]: 健康风险评估结果列表和总记录数
        """
        try:
            query_conditions = []
            query_params = []
            
            # 处理过滤条件
            if "user_id" in filters:
                query_conditions.append("user_id = %s")
                query_params.append(filters["user_id"])
                
            if "risk_level" in filters:
                query_conditions.append("risk_level = %s")
                risk_level_value = filters["risk_level"].value if isinstance(filters["risk_level"], RiskLevel) else filters["risk_level"]
                query_params.append(risk_level_value)
                
            if "start_date" in filters:
                query_conditions.append("assessment_date >= %s")
                query_params.append(filters["start_date"])
                
            if "end_date" in filters:
                query_conditions.append("assessment_date <= %s")
                query_params.append(filters["end_date"])
            
            # 构建查询条件
            where_clause = ""
            if query_conditions:
                where_clause = "WHERE " + " AND ".join(query_conditions)
            
            # 计算总记录数
            count_query = f"SELECT COUNT(*) as total FROM health_risk_assessments {where_clause}"
            
            # 查询分页数据
            offset = (page - 1) * page_size
            data_query = f'''
            SELECT * FROM health_risk_assessments
            {where_clause}
            ORDER BY assessment_date DESC
            LIMIT %s OFFSET %s
            '''
            query_params.extend([page_size, offset])
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # 获取总记录数
                    cursor.execute(count_query, query_params[:-2] if query_params else None)
                    total = cursor.fetchone()["total"]
                    
                    # 获取分页数据
                    cursor.execute(data_query, query_params)
                    results = cursor.fetchall()
                    
                    # 转换为领域模型
                    assessments = []
                    for result in results:
                        # 使用现有的get_assessment_by_id方法获取完整的对象
                        assessment = self.get_assessment_by_id(result["id"])
                        if assessment:
                            assessments.append(assessment)
                    
                    return assessments, total
        except Exception as e:
            logger.error(f"Error listing health risk assessments: {str(e)}")
            raise