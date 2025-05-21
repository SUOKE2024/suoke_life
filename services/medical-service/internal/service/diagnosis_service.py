#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from internal.model.diagnosis import (
    DiagnosisRequest, DiagnosisResult, DiagnosisStatus,
    TCMDiagnosis, WesternDiagnosis, LookDiagnosis, ListenSmellDiagnosis,
    InquiryDiagnosis, PalpationDiagnosis, LabTest
)
from pkg.utils.observability import trace_method, measure_time

logger = logging.getLogger(__name__)

class DiagnosisService:
    """诊断服务实现"""
    
    def __init__(self, repository, service_config):
        """
        初始化诊断服务
        
        Args:
            repository: 诊断仓库
            service_config: 服务配置，包含依赖服务的配置
        """
        self.repository = repository
        self.service_config = service_config
    
    @trace_method
    def request_diagnosis(self, user_id: str, chief_complaint: str, 
                        symptoms: Optional[List[str]] = None,
                        health_data: Optional[Dict[str, str]] = None,
                        diagnostic_methods: Optional[List[str]] = None,
                        include_western_medicine: bool = True,
                        include_tcm: bool = True) -> str:
        """
        请求诊断
        
        Args:
            user_id: A用户ID
            chief_complaint: 主诉
            symptoms: 症状列表
            health_data: 健康数据，如 {"heart_rate": "85"}
            diagnostic_methods: 诊断方法，如 ["望", "闻", "问", "切"]
            include_western_medicine: 是否包含西医诊断
            include_tcm: 是否包含中医诊断
            
        Returns:
            str: 诊断ID
        """
        with measure_time("请求诊断"):
            logger.info(f"为用户 {user_id} 请求诊断")
            
            # 创建诊断请求
            diagnosis_request = DiagnosisRequest.create(
                user_id=user_id,
                chief_complaint=chief_complaint,
                symptoms=symptoms,
                health_data=health_data,
                diagnostic_methods=diagnostic_methods,
                include_western_medicine=include_western_medicine,
                include_tcm=include_tcm
            )
            
            # 创建待处理的诊断结果
            diagnosis_result = DiagnosisResult.create_pending(user_id)
            
            # 存储诊断请求和初始结果
            self.repository.save_request(diagnosis_request)
            self.repository.save_result(diagnosis_result)
            
            # 异步处理诊断（这里简化为直接处理）
            # 实际应用中，可能会将请求放入队列，由后台任务处理
            self._process_diagnosis(diagnosis_request.id, diagnosis_result.id)
            
            return diagnosis_result.id
    
    @trace_method
    def get_diagnosis_result(self, diagnosis_id: str) -> Optional[DiagnosisResult]:
        """
        获取诊断结果
        
        Args:
            diagnosis_id: 诊断ID
            
        Returns:
            Optional[DiagnosisResult]: 诊断结果，如果不存在则返回None
        """
        logger.info(f"获取诊断结果 {diagnosis_id}")
        return self.repository.get_result_by_id(diagnosis_id)
    
    @trace_method
    def list_diagnosis_history(self, user_id: str, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None, page: int = 1,
                             page_size: int = 10) -> tuple[List[DiagnosisResult], int]:
        """
        列出诊断历史
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            page: 页码
            page_size: 每页记录数
            
        Returns:
            Tuple[List[DiagnosisResult], int]: 诊断结果列表和总记录数
        """
        logger.info(f"列出用户 {user_id} 的诊断历史")
        
        filters = {
            "user_id": user_id
        }
        
        if start_date:
            filters["start_date"] = start_date
            
        if end_date:
            filters["end_date"] = end_date
        
        return self.repository.list_results(filters, page, page_size)
    
    def _process_diagnosis(self, request_id: str, result_id: str) -> None:
        """
        处理诊断请求
        
        Args:
            request_id: 诊断请求ID
            result_id: 诊断结果ID
        """
        logger.info(f"处理诊断请求 {request_id} 和结果 {result_id}")
        
        try:
            # 获取诊断请求和初始结果
            diagnosis_request = self.repository.get_request_by_id(request_id)
            diagnosis_result = self.repository.get_result_by_id(result_id)
            
            if not diagnosis_request or not diagnosis_result:
                logger.error(f"诊断请求或结果不存在: request_id={request_id}, result_id={result_id}")
                return
            
            # 调用外部服务获取诊断结果
            tcm_diagnosis = None
            western_diagnosis = None
            
            # 中医诊断
            if diagnosis_request.include_tcm:
                tcm_diagnosis = self._get_tcm_diagnosis(
                    diagnosis_request.user_id,
                    diagnosis_request.chief_complaint,
                    diagnosis_request.symptoms,
                    diagnosis_request.health_data,
                    diagnosis_request.diagnostic_methods
                )
            
            # 西医诊断
            if diagnosis_request.include_western_medicine:
                western_diagnosis = self._get_western_diagnosis(
                    diagnosis_request.user_id,
                    diagnosis_request.chief_complaint,
                    diagnosis_request.symptoms,
                    diagnosis_request.health_data
                )
            
            # 综合结果
            integrated_diagnosis = self._generate_integrated_diagnosis(
                tcm_diagnosis, western_diagnosis
            )
            
            # 健康建议
            health_advice = self._generate_health_advice(
                tcm_diagnosis, western_diagnosis
            )
            
            # 更新诊断结果
            diagnosis_result.complete(
                tcm_diagnosis=tcm_diagnosis,
                western_diagnosis=western_diagnosis,
                integrated_diagnosis=integrated_diagnosis,
                health_advice=health_advice
            )
            
            # 保存更新后的结果
            self.repository.update_result(diagnosis_result)
            logger.info(f"完成诊断 {result_id}")
            
        except Exception as e:
            logger.error(f"处理诊断时发生错误: {str(e)}")
            # 获取诊断结果并标记为失败
            try:
                diagnosis_result = self.repository.get_result_by_id(result_id)
                if diagnosis_result:
                    diagnosis_result.fail()
                    self.repository.update_result(diagnosis_result)
            except Exception as update_error:
                logger.error(f"更新诊断结果状态时发生错误: {str(update_error)}")
    
    def _get_tcm_diagnosis(self, user_id: str, chief_complaint: str,
                         symptoms: List[str], health_data: Dict[str, str],
                         diagnostic_methods: List[str]) -> TCMDiagnosis:
        """
        获取中医诊断结果
        
        实际应用中，应该调用四诊服务获取结果
        这里为演示提供一个简化的实现
        
        Args:
            user_id: 用户ID
            chief_complaint: 主诉
            symptoms: 症状列表
            health_data: 健康数据
            diagnostic_methods: 诊断方法
            
        Returns:
            TCMDiagnosis: 中医诊断结果
        """
        logger.info(f"获取用户 {user_id} 的中医诊断")
        
        # 创建四诊结果
        look = None
        listen_smell = None
        inquiry = None
        palpation = None
        
        # 如果包含望诊
        if "望" in diagnostic_methods:
            look = LookDiagnosis(
                facial_color="偏黄",
                tongue_diagnosis="舌质淡红，苔薄白",
                body_shape="中等体型",
                complexion="面色晦暗",
                abnormal_signs=[]
            )
        
        # 如果包含闻诊
        if "闻" in diagnostic_methods:
            listen_smell = ListenSmellDiagnosis(
                voice_quality="声音低沉",
                breathing_sounds="呼吸平稳",
                odor="口气微甜",
                abnormal_sounds=[]
            )
        
        # 如果包含问诊
        if "问" in diagnostic_methods:
            inquiry = InquiryDiagnosis(
                reported_symptoms=symptoms,
                sleep_quality="入睡困难，易醒",
                diet_habits="胃口一般，喜热食",
                emotional_state="容易焦虑",
                pain_description=chief_complaint,
                additional_information={}
            )
        
        # 如果包含切诊
        if "切" in diagnostic_methods:
            palpation = PalpationDiagnosis(
                pulse_diagnosis="脉沉细",
                pulse_qualities=["沉", "细", "弱"],
                abdominal_diagnosis="腹部柔软，无压痛",
                acupoint_tenderness={},
                other_findings=[]
            )
        
        # 创建中医诊断结果
        tcm_diagnosis = TCMDiagnosis(
            look=look,
            listen_smell=listen_smell,
            inquiry=inquiry,
            palpation=palpation,
            pattern_differentiation=["气虚", "阴虚"],
            meridian_analysis=["脾经不足", "肝经郁滞"],
            constitution_type="气虚质",
            imbalances=["气虚", "血瘀"]
        )
        
        return tcm_diagnosis
    
    def _get_western_diagnosis(self, user_id: str, chief_complaint: str,
                             symptoms: List[str], health_data: Dict[str, str]) -> WesternDiagnosis:
        """
        获取西医诊断结果
        
        实际应用中，应该调用西医诊断服务获取结果
        这里为演示提供一个简化的实现
        
        Args:
            user_id: 用户ID
            chief_complaint: 主诉
            symptoms: 症状列表
            health_data: 健康数据
            
        Returns:
            WesternDiagnosis: 西医诊断结果
        """
        logger.info(f"获取用户 {user_id} 的西医诊断")
        
        # 解析健康数据
        vital_signs = {}
        for key, value in health_data.items():
            if key in ["heart_rate", "blood_pressure", "temperature", "respiratory_rate", "oxygen_saturation"]:
                vital_signs[key] = value
        
        # 创建实验室检测结果
        lab_results = [
            LabTest(
                test_name="血常规",
                result="正常",
                unit="",
                reference_range="正常范围",
                is_abnormal=False
            ),
            LabTest(
                test_name="血糖",
                result="5.8",
                unit="mmol/L",
                reference_range="3.9-6.1",
                is_abnormal=False
            )
        ]
        
        # 创建西医诊断结果
        western_diagnosis = WesternDiagnosis(
            possible_conditions=["慢性疲劳综合征", "焦虑症"],
            vital_signs=vital_signs,
            lab_results=lab_results,
            clinical_analysis="患者表现为持续性疲劳，伴有轻度焦虑症状，血液检查基本正常",
            confidence_score=85,
            differential_diagnosis=["抑郁症", "贫血", "甲状腺功能减退"]
        )
        
        return western_diagnosis
    
    def _generate_integrated_diagnosis(self, tcm_diagnosis: Optional[TCMDiagnosis],
                                    western_diagnosis: Optional[WesternDiagnosis]) -> str:
        """
        生成综合诊断结果
        
        Args:
            tcm_diagnosis: 中医诊断结果
            western_diagnosis: 西医诊断结果
            
        Returns:
            str: 综合诊断结果
        """
        integrated_result = []
        
        # 添加西医诊断
        if western_diagnosis:
            integrated_result.append("西医诊断：")
            for condition in western_diagnosis.possible_conditions:
                integrated_result.append(f"- {condition}")
            
            if western_diagnosis.clinical_analysis:
                integrated_result.append(f"\n临床分析：{western_diagnosis.clinical_analysis}")
        
        # 添加中医诊断
        if tcm_diagnosis:
            integrated_result.append("\n中医辨证：")
            for pattern in tcm_diagnosis.pattern_differentiation:
                integrated_result.append(f"- {pattern}")
            
            if tcm_diagnosis.constitution_type:
                integrated_result.append(f"\n体质类型：{tcm_diagnosis.constitution_type}")
        
        # 综合结论
        integrated_result.append("\n综合结论：")
        if western_diagnosis and tcm_diagnosis:
            integrated_result.append("患者从西医角度考虑可能存在慢性疲劳和轻度焦虑，从中医角度表现为气虚、阴虚证。建议结合中西医治疗方案，调整生活方式，增强体质。")
        elif western_diagnosis:
            integrated_result.append("患者从西医角度考虑可能存在慢性疲劳和轻度焦虑。建议进一步检查确认诊断，并遵医嘱进行治疗。")
        elif tcm_diagnosis:
            integrated_result.append("患者从中医角度表现为气虚、阴虚证。建议通过中医治疗调理身体，注意休息，调整饮食结构。")
        
        return "\n".join(integrated_result)
    
    def _generate_health_advice(self, tcm_diagnosis: Optional[TCMDiagnosis],
                             western_diagnosis: Optional[WesternDiagnosis]) -> List[str]:
        """
        生成健康建议
        
        Args:
            tcm_diagnosis: 中医诊断结果
            western_diagnosis: 西医诊断结果
            
        Returns:
            List[str]: 健康建议列表
        """
        advice = []
        
        # 基于西医诊断的建议
        if western_diagnosis:
            advice.extend([
                "保持充足的睡眠，每晚建议睡眠7-8小时",
                "适当进行有氧运动，如散步、慢跑等，每周3-5次，每次30分钟",
                "避免过度劳累和压力，学习放松技巧如深呼吸和冥想",
                "定期复查，监测身体状况变化"
            ])
        
        # 基于中医诊断的建议
        if tcm_diagnosis:
            if "气虚" in tcm_diagnosis.pattern_differentiation:
                advice.extend([
                    "饮食宜清淡易消化，多食用山药、大枣、黑芝麻等补气食物",
                    "适当食用具有健脾益气作用的食物，如红枣、莲子、山药等",
                    "保持良好的作息习惯，避免熬夜",
                    "可进行太极、八段锦等缓和运动，增强体质"
                ])
            
            if "阴虚" in tcm_diagnosis.pattern_differentiation:
                advice.extend([
                    "多食用滋阴润燥的食物，如百合、银耳、梨等",
                    "避免辛辣刺激、油腻、煎炸食物",
                    "保持心情平和，避免大喜大悲",
                    "避免长时间处于干燥环境"
                ])
        
        # 通用健康建议
        advice.extend([
            "保持均衡饮食，多摄入蔬菜水果",
            "保持充足的水分摄入，每天建议饮水1500-2000ml",
            "保持积极乐观的心态，必要时寻求心理咨询"
        ])
        
        return advice