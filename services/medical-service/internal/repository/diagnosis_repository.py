#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

from internal.model.diagnosis import (
    DiagnosisRequest, DiagnosisResult, DiagnosisStatus,
    TCMDiagnosis, WesternDiagnosis, LookDiagnosis, ListenSmellDiagnosis,
    InquiryDiagnosis, PalpationDiagnosis, LabTest
)

logger = logging.getLogger(__name__)


class DiagnosisRepository:
    """诊断仓库实现"""
    
    def __init__(self, db_config):
        """
        初始化诊断仓库
        
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
                    # 创建诊断请求表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS diagnosis_requests (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        chief_complaint TEXT NOT NULL,
                        symptoms JSONB,
                        health_data JSONB,
                        diagnostic_methods JSONB,
                        include_western_medicine BOOLEAN NOT NULL,
                        include_tcm BOOLEAN NOT NULL,
                        created_at TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_diagnosis_requests_user_id ON diagnosis_requests(user_id);
                    ''')
                    
                    # 创建诊断结果表
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS diagnosis_results (
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        diagnosis_time TIMESTAMP NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        tcm_diagnosis JSONB,
                        western_diagnosis JSONB,
                        integrated_diagnosis TEXT,
                        health_advice JSONB,
                        created_at TIMESTAMP NOT NULL
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_diagnosis_results_user_id ON diagnosis_results(user_id);
                    CREATE INDEX IF NOT EXISTS idx_diagnosis_results_diagnosis_time ON diagnosis_results(diagnosis_time);
                    CREATE INDEX IF NOT EXISTS idx_diagnosis_results_status ON diagnosis_results(status);
                    ''')
                conn.commit()
                logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_request(self, request: DiagnosisRequest) -> DiagnosisRequest:
        """
        保存诊断请求
        
        Args:
            request: 诊断请求
            
        Returns:
            DiagnosisRequest: 保存的诊断请求
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO diagnosis_requests (
                        id, user_id, chief_complaint, symptoms, health_data,
                        diagnostic_methods, include_western_medicine, include_tcm, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        request.id, request.user_id, request.chief_complaint,
                        json.dumps(request.symptoms), json.dumps(request.health_data),
                        json.dumps(request.diagnostic_methods),
                        request.include_western_medicine, request.include_tcm,
                        request.created_at
                    ))
                    result = cursor.fetchone()
                conn.commit()
            
            return request
        except Exception as e:
            logger.error(f"Error saving diagnosis request: {str(e)}")
            raise
    
    def get_request_by_id(self, request_id: str) -> Optional[DiagnosisRequest]:
        """
        通过ID获取诊断请求
        
        Args:
            request_id: 请求ID
            
        Returns:
            Optional[DiagnosisRequest]: 诊断请求，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM diagnosis_requests WHERE id = %s', (request_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return DiagnosisRequest(
                            id=result["id"],
                            user_id=result["user_id"],
                            chief_complaint=result["chief_complaint"],
                            symptoms=result["symptoms"],
                            health_data=result["health_data"],
                            diagnostic_methods=result["diagnostic_methods"],
                            include_western_medicine=result["include_western_medicine"],
                            include_tcm=result["include_tcm"],
                            created_at=result["created_at"]
                        )
                    
                    return None
        except Exception as e:
            logger.error(f"Error getting diagnosis request by ID: {str(e)}")
            raise
    
    def save_result(self, result: DiagnosisResult) -> DiagnosisResult:
        """
        保存诊断结果
        
        Args:
            result: 诊断结果
            
        Returns:
            DiagnosisResult: 保存的诊断结果
        """
        try:
            # 转换TCM诊断结果为JSON
            tcm_diagnosis_json = None
            if result.tcm_diagnosis:
                tcm_diagnosis_json = {
                    "look": vars(result.tcm_diagnosis.look) if result.tcm_diagnosis.look else None,
                    "listen_smell": vars(result.tcm_diagnosis.listen_smell) if result.tcm_diagnosis.listen_smell else None,
                    "inquiry": vars(result.tcm_diagnosis.inquiry) if result.tcm_diagnosis.inquiry else None,
                    "palpation": vars(result.tcm_diagnosis.palpation) if result.tcm_diagnosis.palpation else None,
                    "pattern_differentiation": result.tcm_diagnosis.pattern_differentiation,
                    "meridian_analysis": result.tcm_diagnosis.meridian_analysis,
                    "constitution_type": result.tcm_diagnosis.constitution_type,
                    "imbalances": result.tcm_diagnosis.imbalances
                }
            
            # 转换Western诊断结果为JSON
            western_diagnosis_json = None
            if result.western_diagnosis:
                lab_results_json = []
                for lab_test in result.western_diagnosis.lab_results:
                    lab_results_json.append(vars(lab_test))
                
                western_diagnosis_json = {
                    "possible_conditions": result.western_diagnosis.possible_conditions,
                    "vital_signs": result.western_diagnosis.vital_signs,
                    "lab_results": lab_results_json,
                    "clinical_analysis": result.western_diagnosis.clinical_analysis,
                    "confidence_score": result.western_diagnosis.confidence_score,
                    "differential_diagnosis": result.western_diagnosis.differential_diagnosis
                }
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    INSERT INTO diagnosis_results (
                        id, user_id, diagnosis_time, status, tcm_diagnosis,
                        western_diagnosis, integrated_diagnosis, health_advice, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    ''', (
                        result.id, result.user_id, result.diagnosis_time, result.status.value,
                        json.dumps(tcm_diagnosis_json) if tcm_diagnosis_json else None,
                        json.dumps(western_diagnosis_json) if western_diagnosis_json else None,
                        result.integrated_diagnosis, json.dumps(result.health_advice),
                        result.created_at
                    ))
                    db_result = cursor.fetchone()
                conn.commit()
            
            return result
        except Exception as e:
            logger.error(f"Error saving diagnosis result: {str(e)}")
            raise
    
    def update_result(self, result: DiagnosisResult) -> DiagnosisResult:
        """
        更新诊断结果
        
        Args:
            result: 诊断结果
            
        Returns:
            DiagnosisResult: 更新后的诊断结果
        """
        try:
            # 转换TCM诊断结果为JSON
            tcm_diagnosis_json = None
            if result.tcm_diagnosis:
                tcm_diagnosis_json = {
                    "look": vars(result.tcm_diagnosis.look) if result.tcm_diagnosis.look else None,
                    "listen_smell": vars(result.tcm_diagnosis.listen_smell) if result.tcm_diagnosis.listen_smell else None,
                    "inquiry": vars(result.tcm_diagnosis.inquiry) if result.tcm_diagnosis.inquiry else None,
                    "palpation": vars(result.tcm_diagnosis.palpation) if result.tcm_diagnosis.palpation else None,
                    "pattern_differentiation": result.tcm_diagnosis.pattern_differentiation,
                    "meridian_analysis": result.tcm_diagnosis.meridian_analysis,
                    "constitution_type": result.tcm_diagnosis.constitution_type,
                    "imbalances": result.tcm_diagnosis.imbalances
                }
            
            # 转换Western诊断结果为JSON
            western_diagnosis_json = None
            if result.western_diagnosis:
                lab_results_json = []
                for lab_test in result.western_diagnosis.lab_results:
                    lab_results_json.append(vars(lab_test))
                
                western_diagnosis_json = {
                    "possible_conditions": result.western_diagnosis.possible_conditions,
                    "vital_signs": result.western_diagnosis.vital_signs,
                    "lab_results": lab_results_json,
                    "clinical_analysis": result.western_diagnosis.clinical_analysis,
                    "confidence_score": result.western_diagnosis.confidence_score,
                    "differential_diagnosis": result.western_diagnosis.differential_diagnosis
                }
            
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                    UPDATE diagnosis_results SET
                        status = %s,
                        tcm_diagnosis = %s,
                        western_diagnosis = %s,
                        integrated_diagnosis = %s,
                        health_advice = %s
                    WHERE id = %s
                    RETURNING *
                    ''', (
                        result.status.value,
                        json.dumps(tcm_diagnosis_json) if tcm_diagnosis_json else None,
                        json.dumps(western_diagnosis_json) if western_diagnosis_json else None,
                        result.integrated_diagnosis,
                        json.dumps(result.health_advice),
                        result.id
                    ))
                    db_result = cursor.fetchone()
                    
                    if not db_result:
                        raise ValueError(f"Diagnosis result with ID {result.id} not found")
                    
                conn.commit()
            
            return result
        except Exception as e:
            logger.error(f"Error updating diagnosis result: {str(e)}")
            raise
    
    def get_result_by_id(self, result_id: str) -> Optional[DiagnosisResult]:
        """
        通过ID获取诊断结果
        
        Args:
            result_id: 结果ID
            
        Returns:
            Optional[DiagnosisResult]: 诊断结果，如果不存在则返回None
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('SELECT * FROM diagnosis_results WHERE id = %s', (result_id,))
                    result = cursor.fetchone()
                    
                    if not result:
                        return None
                    
                    # 解析状态
                    status = DiagnosisStatus(result["status"])
                    
                    # 解析TCM诊断
                    tcm_diagnosis = None
                    if result["tcm_diagnosis"]:
                        tcm_json = result["tcm_diagnosis"]
                        
                        # 解析望诊
                        look = None
                        if tcm_json.get("look"):
                            look = LookDiagnosis(
                                facial_color=tcm_json["look"].get("facial_color"),
                                tongue_diagnosis=tcm_json["look"].get("tongue_diagnosis"),
                                body_shape=tcm_json["look"].get("body_shape"),
                                complexion=tcm_json["look"].get("complexion"),
                                abnormal_signs=tcm_json["look"].get("abnormal_signs", [])
                            )
                        
                        # 解析闻诊
                        listen_smell = None
                        if tcm_json.get("listen_smell"):
                            listen_smell = ListenSmellDiagnosis(
                                voice_quality=tcm_json["listen_smell"].get("voice_quality"),
                                breathing_sounds=tcm_json["listen_smell"].get("breathing_sounds"),
                                odor=tcm_json["listen_smell"].get("odor"),
                                abnormal_sounds=tcm_json["listen_smell"].get("abnormal_sounds", [])
                            )
                        
                        # 解析问诊
                        inquiry = None
                        if tcm_json.get("inquiry"):
                            inquiry = InquiryDiagnosis(
                                reported_symptoms=tcm_json["inquiry"].get("reported_symptoms", []),
                                sleep_quality=tcm_json["inquiry"].get("sleep_quality"),
                                diet_habits=tcm_json["inquiry"].get("diet_habits"),
                                emotional_state=tcm_json["inquiry"].get("emotional_state"),
                                pain_description=tcm_json["inquiry"].get("pain_description"),
                                additional_information=tcm_json["inquiry"].get("additional_information", {})
                            )
                        
                        # 解析切诊
                        palpation = None
                        if tcm_json.get("palpation"):
                            palpation = PalpationDiagnosis(
                                pulse_diagnosis=tcm_json["palpation"].get("pulse_diagnosis"),
                                pulse_qualities=tcm_json["palpation"].get("pulse_qualities", []),
                                abdominal_diagnosis=tcm_json["palpation"].get("abdominal_diagnosis"),
                                acupoint_tenderness=tcm_json["palpation"].get("acupoint_tenderness", {}),
                                other_findings=tcm_json["palpation"].get("other_findings", [])
                            )
                        
                        tcm_diagnosis = TCMDiagnosis(
                            look=look,
                            listen_smell=listen_smell,
                            inquiry=inquiry,
                            palpation=palpation,
                            pattern_differentiation=tcm_json.get("pattern_differentiation", []),
                            meridian_analysis=tcm_json.get("meridian_analysis", []),
                            constitution_type=tcm_json.get("constitution_type"),
                            imbalances=tcm_json.get("imbalances", [])
                        )
                    
                    # 解析Western诊断
                    western_diagnosis = None
                    if result["western_diagnosis"]:
                        western_json = result["western_diagnosis"]
                        
                        # 解析实验室检测结果
                        lab_results = []
                        if "lab_results" in western_json:
                            for lab_test_json in western_json["lab_results"]:
                                lab_results.append(LabTest(
                                    test_name=lab_test_json["test_name"],
                                    result=lab_test_json["result"],
                                    unit=lab_test_json["unit"],
                                    reference_range=lab_test_json["reference_range"],
                                    is_abnormal=lab_test_json["is_abnormal"]
                                ))
                        
                        western_diagnosis = WesternDiagnosis(
                            possible_conditions=western_json.get("possible_conditions", []),
                            vital_signs=western_json.get("vital_signs", {}),
                            lab_results=lab_results,
                            clinical_analysis=western_json.get("clinical_analysis"),
                            confidence_score=western_json.get("confidence_score", 0),
                            differential_diagnosis=western_json.get("differential_diagnosis", [])
                        )
                    
                    # 创建诊断结果
                    diagnosis_result = DiagnosisResult(
                        id=result["id"],
                        user_id=result["user_id"],
                        diagnosis_time=result["diagnosis_time"],
                        status=status,
                        tcm_diagnosis=tcm_diagnosis,
                        western_diagnosis=western_diagnosis,
                        integrated_diagnosis=result["integrated_diagnosis"],
                        health_advice=result["health_advice"] if result["health_advice"] else [],
                        created_at=result["created_at"]
                    )
                    
                    return diagnosis_result
        except Exception as e:
            logger.error(f"Error getting diagnosis result by ID: {str(e)}")
            raise
    
    def list_results(self, filters: Dict[str, Any], page: int = 1, page_size: int = 10) -> Tuple[List[DiagnosisResult], int]:
        """
        列出诊断结果
        
        Args:
            filters: 过滤条件
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[DiagnosisResult], int]: 诊断结果列表和总记录数
        """
        try:
            query_conditions = []
            query_params = []
            
            # 处理过滤条件
            if "user_id" in filters:
                query_conditions.append("user_id = %s")
                query_params.append(filters["user_id"])
                
            if "status" in filters:
                query_conditions.append("status = %s")
                query_params.append(filters["status"].value if isinstance(filters["status"], DiagnosisStatus) else filters["status"])
                
            if "start_date" in filters:
                query_conditions.append("diagnosis_time >= %s")
                query_params.append(filters["start_date"])
                
            if "end_date" in filters:
                query_conditions.append("diagnosis_time <= %s")
                query_params.append(filters["end_date"])
            
            # 构建查询条件
            where_clause = ""
            if query_conditions:
                where_clause = "WHERE " + " AND ".join(query_conditions)
            
            # 计算总记录数
            count_query = f"SELECT COUNT(*) as total FROM diagnosis_results {where_clause}"
            
            # 查询分页数据
            offset = (page - 1) * page_size
            data_query = f'''
            SELECT * FROM diagnosis_results
            {where_clause}
            ORDER BY diagnosis_time DESC
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
                    diagnosis_results = []
                    for result in results:
                        # 使用现有的get_result_by_id方法获取完整的对象
                        diagnosis_result = self.get_result_by_id(result["id"])
                        if diagnosis_result:
                            diagnosis_results.append(diagnosis_result)
                    
                    return diagnosis_results, total
        except Exception as e:
            logger.error(f"Error listing diagnosis results: {str(e)}")
            raise