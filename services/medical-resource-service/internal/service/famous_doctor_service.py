"""
名医资源管理服务
提供名医认证、资源管理、专长分析等功能
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)


class FamousDoctorLevel(Enum):
    """名医等级"""
    NATIONAL_MASTER = "国医大师"
    PROVINCIAL_MASTER = "省级名医"
    MUNICIPAL_EXPERT = "市级专家"
    HOSPITAL_CHIEF = "院级主任"
    SENIOR_SPECIALIST = "资深专家"


class CertificationStatus(Enum):
    """认证状态"""
    PENDING = "待认证"
    APPROVED = "已认证"
    REJECTED = "已拒绝"
    EXPIRED = "已过期"
    SUSPENDED = "已暂停"


class SpecialtyLevel(Enum):
    """专长等级"""
    MASTER = "大师级"
    EXPERT = "专家级"
    PROFICIENT = "熟练级"
    BASIC = "基础级"


@dataclass
class Certification:
    """认证信息"""
    certification_id: str
    doctor_id: str
    level: FamousDoctorLevel
    authority: str  # 认证机构
    certificate_number: str
    issue_date: datetime
    expiry_date: datetime
    status: CertificationStatus
    verification_documents: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Specialty:
    """专长信息"""
    specialty_id: str
    name: str
    description: str
    level: SpecialtyLevel
    years_of_experience: int
    case_count: int
    success_rate: float
    representative_cases: List[str] = field(default_factory=list)
    research_papers: List[str] = field(default_factory=list)
    awards: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    """成就信息"""
    achievement_id: str
    title: str
    description: str
    category: str  # 学术、临床、社会贡献等
    date: datetime
    issuing_organization: str
    significance_level: int  # 1-5级，5为最高
    evidence_documents: List[str] = field(default_factory=list)


@dataclass
class FamousDoctor:
    """名医信息"""
    doctor_id: str
    name: str
    gender: str
    birth_date: datetime
    photo_url: str
    biography: str
    
    # 认证信息
    certifications: List[Certification] = field(default_factory=list)
    highest_level: Optional[FamousDoctorLevel] = None
    
    # 专业信息
    specialties: List[Specialty] = field(default_factory=list)
    primary_specialty: Optional[str] = None
    medical_school: str = ""
    graduation_year: int = 0
    
    # 执业信息
    license_number: str = ""
    practice_years: int = 0
    current_hospital: str = ""
    department: str = ""
    position: str = ""
    
    # 学术成就
    achievements: List[Achievement] = field(default_factory=list)
    academic_titles: List[str] = field(default_factory=list)
    research_interests: List[str] = field(default_factory=list)
    
    # 临床数据
    total_patients_treated: int = 0
    average_rating: float = 0.0
    review_count: int = 0
    consultation_fee: float = 0.0
    
    # 可用性
    is_active: bool = True
    is_accepting_patients: bool = True
    max_daily_appointments: int = 20
    
    # 联系信息
    contact_info: Dict[str, str] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DoctorSearchCriteria:
    """医生搜索条件"""
    keywords: Optional[str] = None
    specialty: Optional[str] = None
    level: Optional[FamousDoctorLevel] = None
    location: Optional[str] = None
    min_rating: Optional[float] = None
    max_fee: Optional[float] = None
    availability_date: Optional[datetime] = None
    sort_by: str = "rating"  # rating, fee, experience
    sort_order: str = "desc"  # asc, desc
    limit: int = 10


@dataclass
class DoctorRecommendation:
    """医生推荐"""
    doctor: FamousDoctor
    match_score: float
    recommendation_reasons: List[str]
    estimated_wait_time: int  # 预计等待天数
    next_available_slot: Optional[datetime] = None


class FamousDoctorService:
    """名医资源管理服务"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化名医资源管理服务

        Args:
            config: 配置信息
        """
        self.config = config
        self.famous_doctors: Dict[str, FamousDoctor] = {}
        self.certifications: Dict[str, Certification] = {}
        
        # 索引
        self.specialty_index: Dict[str, set] = {}
        self.level_index: Dict[FamousDoctorLevel, set] = {}
        self.location_index: Dict[str, set] = {}
        
        # 配置参数
        self.search_config = {
            "max_results": 50,
            "default_sort": "rating",
            "score_weights": {
                "specialty_match": 0.3,
                "level_importance": 0.25,
                "rating": 0.2,
                "experience": 0.15,
                "availability": 0.1
            }
        }
        
        # 初始化示例数据
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """初始化示例数据"""
        # 创建示例名医
        sample_doctors = [
            {
                "doctor_id": str(uuid.uuid4()),
                "name": "王国维",
                "gender": "男",
                "birth_date": datetime(1955, 3, 15),
                "biography": "国医大师，中医内科专家，从事中医临床工作40余年，擅长治疗心血管疾病、糖尿病等慢性病。",
                "medical_school": "北京中医药大学",
                "graduation_year": 1978,
                "license_number": "110101195503151234",
                "practice_years": 45,
                "current_hospital": "中国中医科学院广安门医院",
                "department": "心血管科",
                "position": "主任医师",
                "total_patients_treated": 50000,
                "average_rating": 4.9,
                "review_count": 2500,
                "consultation_fee": 500.0,
                "level": FamousDoctorLevel.NATIONAL_MASTER,
                "specialties": ["心血管疾病", "糖尿病", "高血压"],
                "achievements": ["国医大师", "全国名中医", "中医药科技进步奖一等奖"]
            },
            {
                "doctor_id": str(uuid.uuid4()),
                "name": "李明华",
                "gender": "女",
                "birth_date": datetime(1960, 8, 22),
                "biography": "省级名医，中医妇科专家，在妇科疾病治疗方面有独特见解，特别擅长不孕不育治疗。",
                "medical_school": "上海中医药大学",
                "graduation_year": 1983,
                "license_number": "310101196008221234",
                "practice_years": 40,
                "current_hospital": "上海市中医医院",
                "department": "妇科",
                "position": "主任医师",
                "total_patients_treated": 30000,
                "average_rating": 4.8,
                "review_count": 1800,
                "consultation_fee": 300.0,
                "level": FamousDoctorLevel.PROVINCIAL_MASTER,
                "specialties": ["妇科疾病", "不孕不育", "月经不调"],
                "achievements": ["省级名中医", "妇科疾病研究突出贡献奖"]
            },
            {
                "doctor_id": str(uuid.uuid4()),
                "name": "张德胜",
                "gender": "男",
                "birth_date": datetime(1965, 12, 10),
                "biography": "市级专家，中医骨科专家，在骨伤科治疗方面经验丰富，擅长运用传统中医手法治疗各种骨科疾病。",
                "medical_school": "广州中医药大学",
                "graduation_year": 1988,
                "license_number": "440101196512101234",
                "practice_years": 35,
                "current_hospital": "广东省中医院",
                "department": "骨科",
                "position": "主任医师",
                "total_patients_treated": 25000,
                "average_rating": 4.7,
                "review_count": 1200,
                "consultation_fee": 200.0,
                "level": FamousDoctorLevel.MUNICIPAL_EXPERT,
                "specialties": ["骨科疾病", "颈椎病", "腰椎间盘突出"],
                "achievements": ["市级名中医", "骨科治疗创新奖"]
            }
        ]
        
        for doctor_data in sample_doctors:
            doctor = self._create_famous_doctor_from_data(doctor_data)
            self.famous_doctors[doctor.doctor_id] = doctor
            self._update_indexes(doctor)

    def _create_famous_doctor_from_data(self, data: Dict[str, Any]) -> FamousDoctor:
        """从数据创建名医对象"""
        doctor = FamousDoctor(
            doctor_id=data["doctor_id"],
            name=data["name"],
            gender=data["gender"],
            birth_date=data["birth_date"],
            photo_url=f"/images/doctors/{data['name']}.jpg",
            biography=data["biography"],
            medical_school=data["medical_school"],
            graduation_year=data["graduation_year"],
            license_number=data["license_number"],
            practice_years=data["practice_years"],
            current_hospital=data["current_hospital"],
            department=data["department"],
            position=data["position"],
            total_patients_treated=data["total_patients_treated"],
            average_rating=data["average_rating"],
            review_count=data["review_count"],
            consultation_fee=data["consultation_fee"],
            highest_level=data["level"]
        )
        
        # 创建认证信息
        certification = Certification(
            certification_id=str(uuid.uuid4()),
            doctor_id=doctor.doctor_id,
            level=data["level"],
            authority="国家中医药管理局" if data["level"] == FamousDoctorLevel.NATIONAL_MASTER else "省中医药管理局",
            certificate_number=f"CERT-{data['level'].value}-{doctor.doctor_id[:8]}",
            issue_date=datetime.now() - timedelta(days=365),
            expiry_date=datetime.now() + timedelta(days=365*5),
            status=CertificationStatus.APPROVED
        )
        doctor.certifications.append(certification)
        self.certifications[certification.certification_id] = certification
        
        # 创建专长信息
        for i, specialty_name in enumerate(data["specialties"]):
            specialty = Specialty(
                specialty_id=str(uuid.uuid4()),
                name=specialty_name,
                description=f"{specialty_name}的诊断和治疗",
                level=SpecialtyLevel.MASTER if i == 0 else SpecialtyLevel.EXPERT,
                years_of_experience=doctor.practice_years - i*5,
                case_count=doctor.total_patients_treated // len(data["specialties"]),
                success_rate=0.85 + i*0.05
            )
            doctor.specialties.append(specialty)
        
        if doctor.specialties:
            doctor.primary_specialty = doctor.specialties[0].name
        
        # 创建成就信息
        for achievement_title in data["achievements"]:
            achievement = Achievement(
                achievement_id=str(uuid.uuid4()),
                title=achievement_title,
                description=f"获得{achievement_title}荣誉称号",
                category="学术荣誉",
                date=datetime.now() - timedelta(days=365*2),
                issuing_organization="国家中医药管理局",
                significance_level=5 if "国医大师" in achievement_title else 4
            )
            doctor.achievements.append(achievement)
        
        # 设置联系信息
        doctor.contact_info = {
            "phone": f"010-{8000 + hash(doctor.doctor_id) % 1000:04d}",
            "email": f"{doctor.name.lower()}@hospital.com",
            "office": f"{doctor.current_hospital}{doctor.department}"
        }
        
        return doctor

    def _update_indexes(self, doctor: FamousDoctor):
        """更新索引"""
        # 专长索引
        for specialty in doctor.specialties:
            if specialty.name not in self.specialty_index:
                self.specialty_index[specialty.name] = set()
            self.specialty_index[specialty.name].add(doctor.doctor_id)
        
        # 等级索引
        if doctor.highest_level:
            if doctor.highest_level not in self.level_index:
                self.level_index[doctor.highest_level] = set()
            self.level_index[doctor.highest_level].add(doctor.doctor_id)
        
        # 地点索引
        location = doctor.current_hospital
        if location not in self.location_index:
            self.location_index[location] = set()
        self.location_index[location].add(doctor.doctor_id)

    async def register_famous_doctor(self, doctor_data: Dict[str, Any]) -> str:
        """
        注册名医

        Args:
            doctor_data: 医生信息

        Returns:
            医生ID
        """
        try:
            logger.info(f"开始注册名医: {doctor_data.get('name')}")
            
            doctor_id = str(uuid.uuid4())
            doctor_data["doctor_id"] = doctor_id
            
            doctor = FamousDoctor(
                doctor_id=doctor_id,
                name=doctor_data["name"],
                gender=doctor_data["gender"],
                birth_date=datetime.fromisoformat(doctor_data["birth_date"]),
                biography=doctor_data.get("biography", ""),
                medical_school=doctor_data.get("medical_school", ""),
                graduation_year=doctor_data.get("graduation_year", 0),
                license_number=doctor_data["license_number"],
                current_hospital=doctor_data.get("current_hospital", ""),
                department=doctor_data.get("department", ""),
                position=doctor_data.get("position", ""),
                consultation_fee=doctor_data.get("consultation_fee", 0.0)
            )
            
            self.famous_doctors[doctor_id] = doctor
            self._update_indexes(doctor)
            
            logger.info(f"名医注册成功，ID: {doctor_id}")
            return doctor_id
            
        except Exception as e:
            logger.error(f"注册名医失败: {e}")
            raise

    async def apply_for_certification(
        self, 
        doctor_id: str, 
        level: FamousDoctorLevel, 
        authority: str,
        documents: List[str]
    ) -> str:
        """
        申请认证

        Args:
            doctor_id: 医生ID
            level: 申请等级
            authority: 认证机构
            documents: 证明文件

        Returns:
            认证ID
        """
        try:
            logger.info(f"医生 {doctor_id} 申请 {level.value} 认证")
            
            if doctor_id not in self.famous_doctors:
                raise ValueError("医生不存在")
            
            certification_id = str(uuid.uuid4())
            certification = Certification(
                certification_id=certification_id,
                doctor_id=doctor_id,
                level=level,
                authority=authority,
                certificate_number=f"CERT-{level.value}-{certification_id[:8]}",
                issue_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=365*5),
                status=CertificationStatus.PENDING,
                verification_documents=documents
            )
            
            self.certifications[certification_id] = certification
            self.famous_doctors[doctor_id].certifications.append(certification)
            
            logger.info(f"认证申请提交成功，认证ID: {certification_id}")
            return certification_id
            
        except Exception as e:
            logger.error(f"申请认证失败: {e}")
            raise

    async def approve_certification(self, certification_id: str, reviewer_id: str) -> bool:
        """
        批准认证

        Args:
            certification_id: 认证ID
            reviewer_id: 审核员ID

        Returns:
            是否成功
        """
        try:
            if certification_id not in self.certifications:
                raise ValueError("认证记录不存在")
            
            certification = self.certifications[certification_id]
            certification.status = CertificationStatus.APPROVED
            
            # 更新医生的最高等级
            doctor = self.famous_doctors[certification.doctor_id]
            if not doctor.highest_level or self._compare_levels(certification.level, doctor.highest_level) > 0:
                doctor.highest_level = certification.level
                self._update_indexes(doctor)
            
            logger.info(f"认证 {certification_id} 已批准")
            return True
            
        except Exception as e:
            logger.error(f"批准认证失败: {e}")
            return False

    def _compare_levels(self, level1: FamousDoctorLevel, level2: FamousDoctorLevel) -> int:
        """比较等级高低"""
        level_order = {
            FamousDoctorLevel.NATIONAL_MASTER: 5,
            FamousDoctorLevel.PROVINCIAL_MASTER: 4,
            FamousDoctorLevel.MUNICIPAL_EXPERT: 3,
            FamousDoctorLevel.HOSPITAL_CHIEF: 2,
            FamousDoctorLevel.SENIOR_SPECIALIST: 1
        }
        
        return level_order.get(level1, 0) - level_order.get(level2, 0)

    async def search_famous_doctors(self, criteria: DoctorSearchCriteria) -> List[FamousDoctor]:
        """
        搜索名医

        Args:
            criteria: 搜索条件

        Returns:
            匹配的名医列表
        """
        try:
            logger.info(f"开始搜索名医，条件: {criteria}")
            
            candidate_ids = set(self.famous_doctors.keys())
            
            # 按专长筛选
            if criteria.specialty:
                specialty_ids = set()
                for specialty, doctor_ids in self.specialty_index.items():
                    if criteria.specialty.lower() in specialty.lower():
                        specialty_ids.update(doctor_ids)
                candidate_ids &= specialty_ids
            
            # 按等级筛选
            if criteria.level:
                level_ids = self.level_index.get(criteria.level, set())
                candidate_ids &= level_ids
            
            # 按地点筛选
            if criteria.location:
                location_ids = set()
                for location, doctor_ids in self.location_index.items():
                    if criteria.location.lower() in location.lower():
                        location_ids.update(doctor_ids)
                candidate_ids &= location_ids
            
            # 获取候选医生
            candidates = [self.famous_doctors[doc_id] for doc_id in candidate_ids]
            
            # 按条件过滤
            filtered_doctors = []
            for doctor in candidates:
                if not doctor.is_active:
                    continue
                
                if criteria.min_rating and doctor.average_rating < criteria.min_rating:
                    continue
                
                if criteria.max_fee and doctor.consultation_fee > criteria.max_fee:
                    continue
                
                if criteria.keywords:
                    keywords_lower = criteria.keywords.lower()
                    if not (keywords_lower in doctor.name.lower() or 
                           keywords_lower in doctor.biography.lower() or
                           any(keywords_lower in spec.name.lower() for spec in doctor.specialties)):
                        continue
                
                filtered_doctors.append(doctor)
            
            # 排序
            filtered_doctors = await self._sort_doctors(filtered_doctors, criteria.sort_by, criteria.sort_order)
            
            # 限制结果数量
            result = filtered_doctors[:criteria.limit]
            
            logger.info(f"搜索完成，找到 {len(result)} 位名医")
            return result
            
        except Exception as e:
            logger.error(f"搜索名医失败: {e}")
            return []

    async def _sort_doctors(self, doctors: List[FamousDoctor], sort_by: str, sort_order: str) -> List[FamousDoctor]:
        """排序医生列表"""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "rating":
            return sorted(doctors, key=lambda d: d.average_rating, reverse=reverse)
        elif sort_by == "fee":
            return sorted(doctors, key=lambda d: d.consultation_fee, reverse=reverse)
        elif sort_by == "experience":
            return sorted(doctors, key=lambda d: d.practice_years, reverse=reverse)
        elif sort_by == "level":
            return sorted(doctors, key=lambda d: self._get_level_score(d.highest_level), reverse=reverse)
        else:
            return doctors

    def _get_level_score(self, level: Optional[FamousDoctorLevel]) -> int:
        """获取等级分数"""
        if not level:
            return 0
        
        level_scores = {
            FamousDoctorLevel.NATIONAL_MASTER: 5,
            FamousDoctorLevel.PROVINCIAL_MASTER: 4,
            FamousDoctorLevel.MUNICIPAL_EXPERT: 3,
            FamousDoctorLevel.HOSPITAL_CHIEF: 2,
            FamousDoctorLevel.SENIOR_SPECIALIST: 1
        }
        
        return level_scores.get(level, 0)

    async def recommend_doctors(
        self, 
        patient_profile: Dict[str, Any], 
        max_recommendations: int = 5
    ) -> List[DoctorRecommendation]:
        """
        推荐医生

        Args:
            patient_profile: 患者档案
            max_recommendations: 最大推荐数量

        Returns:
            医生推荐列表
        """
        try:
            logger.info(f"开始为患者推荐医生")
            
            # 提取患者需求
            symptoms = patient_profile.get("symptoms", [])
            constitution_type = patient_profile.get("constitution_type", "")
            budget_range = patient_profile.get("budget_range", (0, float('inf')))
            location_preference = patient_profile.get("location", "")
            
            recommendations = []
            
            for doctor in self.famous_doctors.values():
                if not doctor.is_active or not doctor.is_accepting_patients:
                    continue
                
                # 计算匹配分数
                match_score = await self._calculate_doctor_match_score(doctor, patient_profile)
                
                if match_score > 0.5:  # 最低匹配阈值
                    # 生成推荐理由
                    reasons = await self._generate_recommendation_reasons(doctor, patient_profile, match_score)
                    
                    # 估算等待时间
                    wait_time = await self._estimate_wait_time(doctor)
                    
                    # 获取下一个可用时段
                    next_slot = await self._get_next_available_slot(doctor)
                    
                    recommendation = DoctorRecommendation(
                        doctor=doctor,
                        match_score=match_score,
                        recommendation_reasons=reasons,
                        estimated_wait_time=wait_time,
                        next_available_slot=next_slot
                    )
                    
                    recommendations.append(recommendation)
            
            # 按匹配分数排序
            recommendations.sort(key=lambda r: r.match_score, reverse=True)
            
            # 限制推荐数量
            result = recommendations[:max_recommendations]
            
            logger.info(f"生成了 {len(result)} 个医生推荐")
            return result
            
        except Exception as e:
            logger.error(f"推荐医生失败: {e}")
            return []

    async def _calculate_doctor_match_score(self, doctor: FamousDoctor, patient_profile: Dict[str, Any]) -> float:
        """计算医生匹配分数"""
        weights = self.search_config["score_weights"]
        total_score = 0.0
        
        # 专长匹配分数
        specialty_score = await self._calculate_specialty_match_score(doctor, patient_profile)
        total_score += specialty_score * weights["specialty_match"]
        
        # 等级重要性分数
        level_score = self._get_level_score(doctor.highest_level) / 5.0
        total_score += level_score * weights["level_importance"]
        
        # 评分分数
        rating_score = doctor.average_rating / 5.0
        total_score += rating_score * weights["rating"]
        
        # 经验分数
        experience_score = min(doctor.practice_years / 30.0, 1.0)
        total_score += experience_score * weights["experience"]
        
        # 可用性分数
        availability_score = 1.0 if doctor.is_accepting_patients else 0.0
        total_score += availability_score * weights["availability"]
        
        return min(total_score, 1.0)

    async def _calculate_specialty_match_score(self, doctor: FamousDoctor, patient_profile: Dict[str, Any]) -> float:
        """计算专长匹配分数"""
        symptoms = patient_profile.get("symptoms", [])
        if not symptoms:
            return 0.5
        
        # 症状与专长的匹配关系
        symptom_specialty_mapping = {
            "胸痛": ["心血管疾病", "心脏病"],
            "头痛": ["神经内科", "中医内科"],
            "失眠": ["中医内科", "神经内科"],
            "月经不调": ["妇科疾病", "妇科"],
            "腰痛": ["骨科疾病", "骨科"],
            "高血压": ["心血管疾病", "内科"],
            "糖尿病": ["内分泌科", "糖尿病"]
        }
        
        match_count = 0
        total_symptoms = len(symptoms)
        
        for symptom in symptoms:
            related_specialties = symptom_specialty_mapping.get(symptom, [])
            for specialty in doctor.specialties:
                if any(related in specialty.name for related in related_specialties):
                    match_count += 1
                    break
        
        return match_count / total_symptoms if total_symptoms > 0 else 0.0

    async def _generate_recommendation_reasons(
        self, doctor: FamousDoctor, patient_profile: Dict[str, Any], match_score: float
    ) -> List[str]:
        """生成推荐理由"""
        reasons = []
        
        # 等级优势
        if doctor.highest_level:
            reasons.append(f"拥有{doctor.highest_level.value}资质")
        
        # 经验优势
        if doctor.practice_years >= 30:
            reasons.append(f"从医{doctor.practice_years}年，经验丰富")
        
        # 评分优势
        if doctor.average_rating >= 4.5:
            reasons.append(f"患者评分{doctor.average_rating}分，口碑优秀")
        
        # 专长匹配
        symptoms = patient_profile.get("symptoms", [])
        for symptom in symptoms:
            for specialty in doctor.specialties:
                if symptom in specialty.name or any(symptom in desc for desc in [specialty.description]):
                    reasons.append(f"擅长治疗{symptom}相关疾病")
                    break
        
        # 成就突出
        if len(doctor.achievements) >= 3:
            reasons.append("学术成就突出，获得多项荣誉")
        
        # 匹配度高
        if match_score >= 0.8:
            reasons.append("综合匹配度极高，强烈推荐")
        
        return reasons

    async def _estimate_wait_time(self, doctor: FamousDoctor) -> int:
        """估算等待时间（天数）"""
        # 基于医生的受欢迎程度估算等待时间
        base_wait_time = 1
        
        # 等级越高，等待时间越长
        if doctor.highest_level == FamousDoctorLevel.NATIONAL_MASTER:
            base_wait_time += 14
        elif doctor.highest_level == FamousDoctorLevel.PROVINCIAL_MASTER:
            base_wait_time += 7
        elif doctor.highest_level == FamousDoctorLevel.MUNICIPAL_EXPERT:
            base_wait_time += 3
        
        # 评分越高，等待时间越长
        if doctor.average_rating >= 4.8:
            base_wait_time += 5
        elif doctor.average_rating >= 4.5:
            base_wait_time += 2
        
        # 费用越高，等待时间可能越长
        if doctor.consultation_fee >= 500:
            base_wait_time += 3
        elif doctor.consultation_fee >= 300:
            base_wait_time += 1
        
        return base_wait_time

    async def _get_next_available_slot(self, doctor: FamousDoctor) -> Optional[datetime]:
        """获取下一个可用时段"""
        # 简单的可用时段计算
        wait_days = await self._estimate_wait_time(doctor)
        next_slot = datetime.now() + timedelta(days=wait_days)
        
        # 调整到工作日的工作时间
        while next_slot.weekday() >= 5:  # 跳过周末
            next_slot += timedelta(days=1)
        
        # 设置为上午9点
        next_slot = next_slot.replace(hour=9, minute=0, second=0, microsecond=0)
        
        return next_slot

    async def get_doctor_details(self, doctor_id: str) -> Optional[FamousDoctor]:
        """获取医生详情"""
        return self.famous_doctors.get(doctor_id)

    async def update_doctor_rating(self, doctor_id: str, rating: float, review_text: str = ""):
        """更新医生评分"""
        if doctor_id in self.famous_doctors:
            doctor = self.famous_doctors[doctor_id]
            
            # 计算新的平均评分
            total_score = doctor.average_rating * doctor.review_count + rating
            doctor.review_count += 1
            doctor.average_rating = total_score / doctor.review_count
            doctor.updated_at = datetime.now()
            
            logger.info(f"医生 {doctor.name} 评分已更新: {doctor.average_rating}")

    async def add_doctor_specialty(self, doctor_id: str, specialty_data: Dict[str, Any]) -> str:
        """添加医生专长"""
        if doctor_id not in self.famous_doctors:
            raise ValueError("医生不存在")
        
        specialty_id = str(uuid.uuid4())
        specialty = Specialty(
            specialty_id=specialty_id,
            name=specialty_data["name"],
            description=specialty_data.get("description", ""),
            level=SpecialtyLevel(specialty_data.get("level", SpecialtyLevel.BASIC.value)),
            years_of_experience=specialty_data.get("years_of_experience", 0),
            case_count=specialty_data.get("case_count", 0),
            success_rate=specialty_data.get("success_rate", 0.0)
        )
        
        doctor = self.famous_doctors[doctor_id]
        doctor.specialties.append(specialty)
        doctor.updated_at = datetime.now()
        
        # 更新索引
        if specialty.name not in self.specialty_index:
            self.specialty_index[specialty.name] = set()
        self.specialty_index[specialty.name].add(doctor_id)
        
        logger.info(f"为医生 {doctor.name} 添加专长: {specialty.name}")
        return specialty_id

    async def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        total_doctors = len(self.famous_doctors)
        active_doctors = sum(1 for d in self.famous_doctors.values() if d.is_active)
        
        # 按等级统计
        level_stats = {}
        for level in FamousDoctorLevel:
            level_stats[level.value] = len(self.level_index.get(level, set()))
        
        # 按专长统计
        specialty_stats = {name: len(ids) for name, ids in self.specialty_index.items()}
        
        # 平均评分
        avg_rating = sum(d.average_rating for d in self.famous_doctors.values()) / total_doctors if total_doctors > 0 else 0
        
        return {
            "total_doctors": total_doctors,
            "active_doctors": active_doctors,
            "level_distribution": level_stats,
            "specialty_distribution": specialty_stats,
            "average_rating": round(avg_rating, 2),
            "total_certifications": len(self.certifications),
            "service_status": "healthy"
        } 