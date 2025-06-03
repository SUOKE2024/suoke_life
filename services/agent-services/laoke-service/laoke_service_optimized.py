#!/usr/bin/env python3
"""
索克生活 - 老克智能体优化服务
基于OptimizedAgentBase实现的中医养生智能体
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from optimized_agent_base import OptimizedAgentBase, AgentRequest, cpu_intensive_task, cached_result
from aiohttp import web

class LaokeOptimizedService(OptimizedAgentBase):
    """老克智能体优化服务 - 中医养生专家"""
    
    def __init__(self):
        super().__init__(
            agent_name="laoke",
            max_workers=int(os.getenv("MAX_WORKERS", "8")),
            redis_url=os.getenv("REDIS_URL"),
            database_url=os.getenv("DATABASE_URL")
        )
        
        # 中医知识库
        self.tcm_knowledge = self._initialize_tcm_knowledge()
    
    def _register_agent_routes(self):
        """注册老克特定路由"""
        self.app.router.add_post("/syndrome_analysis", self._syndrome_analysis_handler)
        self.app.router.add_post("/prescription", self._prescription_handler)
        self.app.router.add_post("/wellness_plan", self._wellness_plan_handler)
        self.app.router.add_get("/knowledge", self._knowledge_handler)
    
    async def _process_action(self, request: AgentRequest) -> Dict[str, Any]:
        """处理老克的具体动作"""
        action = request.action
        input_data = request.input_data
        
        if action == "syndrome_analysis":
            return await self._handle_syndrome_analysis(input_data)
        elif action == "prescription":
            return await self._handle_prescription(input_data)
        elif action == "wellness_plan":
            return await self._handle_wellness_plan(input_data)
        elif action == "constitution_analysis":
            return await self._handle_constitution_analysis(input_data)
        else:
            raise ValueError(f"未知的动作类型: {action}")
    
    @cached_result(ttl=600)
    async def _handle_syndrome_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理中医辨证分析"""
        symptoms = input_data.get("symptoms", [])
        pulse = input_data.get("pulse", "")
        tongue = input_data.get("tongue", "")
        
        # 中医辨证分析
        syndrome_result = await self._analyze_tcm_syndrome(symptoms, pulse, tongue)
        
        # 病机分析
        pathogenesis = await self._analyze_pathogenesis(syndrome_result)
        
        return {
            "syndrome_analysis": syndrome_result,
            "pathogenesis": pathogenesis,
            "treatment_principle": self._determine_treatment_principle(syndrome_result),
            "prognosis": self._assess_prognosis(syndrome_result),
            "timestamp": datetime.now().isoformat()
        }
    
    @cpu_intensive_task
    def _complex_syndrome_calculation(self, symptom_matrix: np.ndarray, 
                                    syndrome_patterns: np.ndarray) -> Dict[str, Any]:
        """复杂辨证计算 - CPU密集型任务"""
        # 症状-证候相关性矩阵计算
        correlation_matrix = np.corrcoef(symptom_matrix, syndrome_patterns)
        
        # 权重计算
        weights = np.random.rand(symptom_matrix.shape[1])
        weighted_scores = np.dot(symptom_matrix, weights)
        
        # 证候匹配度计算
        syndrome_scores = []
        for i, pattern in enumerate(syndrome_patterns):
            similarity = self.algorithms.vector_similarity(
                symptom_matrix.mean(axis=0), pattern
            )
            syndrome_scores.append({
                "syndrome_id": i,
                "score": float(similarity),
                "confidence": float(np.random.rand())
            })
        
        # 排序并返回最匹配的证候
        syndrome_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "top_syndromes": syndrome_scores[:3],
            "correlation_strength": float(np.mean(correlation_matrix)),
            "analysis_confidence": float(np.mean([s["confidence"] for s in syndrome_scores[:3]]))
        }
    
    async def _handle_prescription(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理中药处方请求"""
        syndrome = input_data.get("syndrome", "")
        constitution = input_data.get("constitution", "")
        symptoms = input_data.get("symptoms", [])
        
        # 生成中药处方
        prescription = await self._generate_prescription(syndrome, constitution, symptoms)
        
        # 用药指导
        medication_guidance = self._generate_medication_guidance(prescription)
        
        return {
            "prescription": prescription,
            "medication_guidance": medication_guidance,
            "contraindications": self._check_contraindications(prescription),
            "follow_up": self._suggest_follow_up(syndrome),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_wellness_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理养生计划请求"""
        user_profile = input_data.get("user_profile", {})
        constitution = input_data.get("constitution", "")
        season = input_data.get("season", self._get_current_season())
        
        # 生成个性化养生计划
        wellness_plan = await self._create_wellness_plan(user_profile, constitution, season)
        
        return {
            "wellness_plan": wellness_plan,
            "seasonal_advice": self._get_seasonal_advice(season, constitution),
            "lifestyle_recommendations": self._generate_lifestyle_recommendations(constitution),
            "dietary_guidance": self._generate_dietary_guidance(constitution, season),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_constitution_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理体质分析请求"""
        questionnaire = input_data.get("questionnaire", {})
        physical_data = input_data.get("physical_data", {})
        
        # 体质辨识
        constitution_result = await self._analyze_constitution(questionnaire, physical_data)
        
        return {
            "constitution_analysis": constitution_result,
            "constitution_characteristics": self._get_constitution_characteristics(constitution_result),
            "health_tendencies": self._analyze_health_tendencies(constitution_result),
            "prevention_advice": self._generate_prevention_advice(constitution_result),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_tcm_syndrome(self, symptoms: List[str], pulse: str, tongue: str) -> Dict[str, Any]:
        """中医辨证分析"""
        # 模拟症状向量化
        symptom_vector = np.random.rand(len(symptoms) if symptoms else 10)
        syndrome_patterns = np.random.rand(8, len(symptom_vector))  # 8种常见证候
        
        # 使用CPU密集型任务进行复杂计算
        syndrome_analysis = await self._complex_syndrome_calculation(
            symptom_vector.reshape(1, -1), syndrome_patterns
        )
        
        # 脉象和舌象分析
        pulse_analysis = self._analyze_pulse(pulse)
        tongue_analysis = self._analyze_tongue(tongue)
        
        return {
            "primary_syndrome": syndrome_analysis["top_syndromes"][0] if syndrome_analysis["top_syndromes"] else None,
            "secondary_syndromes": syndrome_analysis["top_syndromes"][1:3],
            "pulse_analysis": pulse_analysis,
            "tongue_analysis": tongue_analysis,
            "confidence": syndrome_analysis["analysis_confidence"]
        }
    
    async def _analyze_pathogenesis(self, syndrome_result: Dict[str, Any]) -> Dict[str, Any]:
        """病机分析"""
        primary_syndrome = syndrome_result.get("primary_syndrome", {})
        
        pathogenesis_map = {
            0: {"name": "气虚", "mechanism": "脾胃虚弱，气血生化不足"},
            1: {"name": "血瘀", "mechanism": "气滞血瘀，经络不通"},
            2: {"name": "痰湿", "mechanism": "脾失健运，水湿内停"},
            3: {"name": "阴虚", "mechanism": "肾阴不足，虚火上炎"},
            4: {"name": "阳虚", "mechanism": "肾阳不足，温煦失职"},
            5: {"name": "肝郁", "mechanism": "肝气郁结，疏泄失常"},
            6: {"name": "心火", "mechanism": "心火亢盛，扰乱神明"},
            7: {"name": "肺燥", "mechanism": "肺阴不足，燥热伤津"}
        }
        
        syndrome_id = primary_syndrome.get("syndrome_id", 0)
        pathogenesis = pathogenesis_map.get(syndrome_id, pathogenesis_map[0])
        
        return {
            "primary_pathogenesis": pathogenesis,
            "disease_location": self._determine_disease_location(syndrome_id),
            "disease_nature": self._determine_disease_nature(syndrome_id),
            "severity": self._assess_severity(primary_syndrome.get("score", 0.5))
        }
    
    async def _generate_prescription(self, syndrome: str, constitution: str, 
                                   symptoms: List[str]) -> Dict[str, Any]:
        """生成中药处方"""
        # 基础方剂库
        base_formulas = {
            "气虚": {
                "name": "四君子汤加减",
                "herbs": [
                    {"name": "人参", "dosage": "9g", "function": "大补元气"},
                    {"name": "白术", "dosage": "9g", "function": "健脾益气"},
                    {"name": "茯苓", "dosage": "9g", "function": "健脾渗湿"},
                    {"name": "甘草", "dosage": "6g", "function": "调和诸药"}
                ]
            },
            "血瘀": {
                "name": "血府逐瘀汤加减",
                "herbs": [
                    {"name": "当归", "dosage": "9g", "function": "活血补血"},
                    {"name": "川芎", "dosage": "6g", "function": "活血行气"},
                    {"name": "红花", "dosage": "9g", "function": "活血通经"},
                    {"name": "桃仁", "dosage": "12g", "function": "活血祛瘀"}
                ]
            }
        }
        
        formula = base_formulas.get(syndrome, base_formulas["气虚"])
        
        return {
            "formula_name": formula["name"],
            "herbs": formula["herbs"],
            "preparation": "水煎服，日一剂，分二次温服",
            "course": "7-14天为一疗程",
            "modifications": self._suggest_modifications(symptoms)
        }
    
    async def _create_wellness_plan(self, user_profile: Dict[str, Any], 
                                  constitution: str, season: str) -> Dict[str, Any]:
        """创建养生计划"""
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "unknown")
        
        plan = {
            "daily_routine": self._create_daily_routine(constitution, season),
            "exercise_plan": self._create_exercise_plan(constitution, age),
            "dietary_plan": self._create_dietary_plan(constitution, season),
            "emotional_care": self._create_emotional_care_plan(constitution),
            "seasonal_adjustments": self._create_seasonal_adjustments(season)
        }
        
        return plan
    
    async def _analyze_constitution(self, questionnaire: Dict[str, Any], 
                                  physical_data: Dict[str, Any]) -> Dict[str, Any]:
        """体质分析"""
        # 九种体质类型
        constitutions = [
            "平和质", "气虚质", "阳虚质", "阴虚质", 
            "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"
        ]
        
        # 模拟体质评分
        scores = np.random.rand(len(constitutions))
        scores = scores / np.sum(scores)  # 归一化
        
        constitution_scores = [
            {"type": const, "score": float(score)}
            for const, score in zip(constitutions, scores)
        ]
        constitution_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "primary_constitution": constitution_scores[0],
            "secondary_constitution": constitution_scores[1] if len(constitution_scores) > 1 else None,
            "constitution_scores": constitution_scores,
            "analysis_confidence": float(np.max(scores))
        }
    
    def _initialize_tcm_knowledge(self) -> Dict[str, Any]:
        """初始化中医知识库"""
        return {
            "syndromes": ["气虚", "血瘀", "痰湿", "阴虚", "阳虚", "肝郁", "心火", "肺燥"],
            "constitutions": ["平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"],
            "herbs": ["人参", "当归", "黄芪", "白术", "茯苓", "川芎", "红花", "桃仁"],
            "acupoints": ["百会", "神门", "三阴交", "足三里", "关元", "气海"]
        }
    
    def _analyze_pulse(self, pulse: str) -> Dict[str, Any]:
        """脉象分析"""
        pulse_types = {
            "浮脉": {"location": "表", "nature": "阳", "indication": "表证"},
            "沉脉": {"location": "里", "nature": "阴", "indication": "里证"},
            "数脉": {"speed": "快", "nature": "热", "indication": "热证"},
            "迟脉": {"speed": "慢", "nature": "寒", "indication": "寒证"}
        }
        
        return pulse_types.get(pulse, {"type": "平脉", "indication": "正常"})
    
    def _analyze_tongue(self, tongue: str) -> Dict[str, Any]:
        """舌象分析"""
        tongue_types = {
            "红舌": {"color": "红", "indication": "热证"},
            "淡舌": {"color": "淡", "indication": "虚证"},
            "紫舌": {"color": "紫", "indication": "瘀证"},
            "厚苔": {"coating": "厚", "indication": "实证"}
        }
        
        return tongue_types.get(tongue, {"type": "正常舌", "indication": "正常"})
    
    def _determine_treatment_principle(self, syndrome_result: Dict[str, Any]) -> str:
        """确定治疗原则"""
        primary_syndrome = syndrome_result.get("primary_syndrome", {})
        syndrome_id = primary_syndrome.get("syndrome_id", 0)
        
        principles = {
            0: "补气健脾",
            1: "活血化瘀",
            2: "化痰祛湿",
            3: "滋阴降火",
            4: "温阳散寒",
            5: "疏肝解郁",
            6: "清心降火",
            7: "润肺止咳"
        }
        
        return principles.get(syndrome_id, "调和阴阳")
    
    def _assess_prognosis(self, syndrome_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估预后"""
        confidence = syndrome_result.get("confidence", 0.5)
        
        if confidence > 0.8:
            prognosis = "良好"
        elif confidence > 0.6:
            prognosis = "较好"
        else:
            prognosis = "需要观察"
        
        return {
            "overall_prognosis": prognosis,
            "recovery_time": "2-4周",
            "factors": ["体质状况", "治疗依从性", "生活方式"]
        }
    
    def _generate_medication_guidance(self, prescription: Dict[str, Any]) -> List[str]:
        """生成用药指导"""
        return [
            "饭后30分钟服用",
            "温水送服",
            "忌食生冷辛辣",
            "如有不适及时就医",
            "定期复诊调方"
        ]
    
    def _check_contraindications(self, prescription: Dict[str, Any]) -> List[str]:
        """检查禁忌症"""
        return [
            "孕妇慎用",
            "过敏体质者慎用",
            "严重肝肾功能不全者禁用"
        ]
    
    def _suggest_follow_up(self, syndrome: str) -> Dict[str, Any]:
        """建议随访"""
        return {
            "follow_up_time": "1周后",
            "observation_points": ["症状改善情况", "不良反应", "舌脉变化"],
            "adjustment_criteria": "根据症状变化调整用药"
        }
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"
    
    def _get_seasonal_advice(self, season: str, constitution: str) -> Dict[str, Any]:
        """获取季节性建议"""
        seasonal_advice = {
            "春": {"principle": "养肝", "activity": "适度运动", "emotion": "保持心情舒畅"},
            "夏": {"principle": "养心", "activity": "避免过度出汗", "emotion": "心静自然凉"},
            "秋": {"principle": "养肺", "activity": "登高远眺", "emotion": "避免悲伤"},
            "冬": {"principle": "养肾", "activity": "早睡晚起", "emotion": "避免恐惧"}
        }
        
        return seasonal_advice.get(season, seasonal_advice["春"])
    
    def _generate_lifestyle_recommendations(self, constitution: str) -> List[str]:
        """生成生活方式建议"""
        recommendations = {
            "气虚质": ["规律作息", "适度运动", "避免过劳"],
            "阳虚质": ["注意保暖", "温补饮食", "避免寒凉"],
            "阴虚质": ["滋阴润燥", "避免熬夜", "心平气和"]
        }
        
        return recommendations.get(constitution, ["保持健康生活方式"])
    
    def _generate_dietary_guidance(self, constitution: str, season: str) -> Dict[str, Any]:
        """生成饮食指导"""
        return {
            "recommended_foods": ["温性食物", "健脾食物", "时令蔬果"],
            "foods_to_avoid": ["生冷食物", "辛辣刺激", "过于油腻"],
            "cooking_methods": ["蒸", "煮", "炖"],
            "meal_timing": "定时定量，细嚼慢咽"
        }
    
    def _determine_disease_location(self, syndrome_id: int) -> str:
        """确定病位"""
        locations = ["脾胃", "心", "肝", "肺", "肾", "胆", "小肠", "大肠"]
        return locations[syndrome_id % len(locations)]
    
    def _determine_disease_nature(self, syndrome_id: int) -> str:
        """确定病性"""
        natures = ["虚", "实", "寒", "热", "虚实夹杂"]
        return natures[syndrome_id % len(natures)]
    
    def _assess_severity(self, score: float) -> str:
        """评估严重程度"""
        if score > 0.8:
            return "重"
        elif score > 0.6:
            return "中"
        else:
            return "轻"
    
    def _suggest_modifications(self, symptoms: List[str]) -> List[str]:
        """建议加减"""
        modifications = []
        
        if "头痛" in symptoms:
            modifications.append("加川芎、白芷")
        if "失眠" in symptoms:
            modifications.append("加酸枣仁、远志")
        if "便秘" in symptoms:
            modifications.append("加大黄、芒硝")
        
        return modifications if modifications else ["根据症状随证加减"]
    
    def _create_daily_routine(self, constitution: str, season: str) -> Dict[str, Any]:
        """创建日常作息"""
        return {
            "wake_time": "6:00-7:00",
            "sleep_time": "22:00-23:00",
            "meal_times": ["7:00", "12:00", "18:00"],
            "rest_periods": ["13:00-14:00"]
        }
    
    def _create_exercise_plan(self, constitution: str, age: int) -> Dict[str, Any]:
        """创建运动计划"""
        return {
            "type": "太极拳、八段锦",
            "frequency": "每日30分钟",
            "intensity": "轻到中等",
            "precautions": ["避免过度出汗", "循序渐进"]
        }
    
    def _create_dietary_plan(self, constitution: str, season: str) -> Dict[str, Any]:
        """创建饮食计划"""
        return {
            "breakfast": "温热粥品",
            "lunch": "营养均衡",
            "dinner": "清淡易消化",
            "snacks": "时令水果",
            "beverages": "温开水、花茶"
        }
    
    def _create_emotional_care_plan(self, constitution: str) -> Dict[str, Any]:
        """创建情志调养计划"""
        return {
            "meditation": "每日10-20分钟",
            "music_therapy": "古典音乐",
            "social_activities": "适度社交",
            "stress_management": "深呼吸、放松训练"
        }
    
    def _create_seasonal_adjustments(self, season: str) -> Dict[str, Any]:
        """创建季节性调整"""
        return {
            "clothing": "根据气温适当增减",
            "activity": "顺应自然规律",
            "diet": "选择时令食材",
            "sleep": "早睡早起"
        }
    
    def _get_constitution_characteristics(self, constitution_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取体质特征"""
        primary_const = constitution_result.get("primary_constitution", {}).get("type", "平和质")
        
        characteristics = {
            "平和质": {"body": "体形匀称", "complexion": "面色润泽", "energy": "精力充沛"},
            "气虚质": {"body": "肌肉松软", "complexion": "面色萎黄", "energy": "容易疲劳"},
            "阳虚质": {"body": "形体白胖", "complexion": "面色㿠白", "energy": "精神不振"}
        }
        
        return characteristics.get(primary_const, characteristics["平和质"])
    
    def _analyze_health_tendencies(self, constitution_result: Dict[str, Any]) -> List[str]:
        """分析健康倾向"""
        primary_const = constitution_result.get("primary_constitution", {}).get("type", "平和质")
        
        tendencies = {
            "气虚质": ["易感冒", "消化不良", "内脏下垂"],
            "阳虚质": ["怕冷", "腹泻", "水肿"],
            "阴虚质": ["口干", "失眠", "便秘"]
        }
        
        return tendencies.get(primary_const, ["身体健康"])
    
    def _generate_prevention_advice(self, constitution_result: Dict[str, Any]) -> List[str]:
        """生成预防建议"""
        return [
            "定期体检",
            "保持良好作息",
            "适度运动",
            "合理饮食",
            "情志调节"
        ]
    
    async def _syndrome_analysis_handler(self, request):
        """辨证分析接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'syn_' + str(hash(str(data)))),
                agent_type="laoke",
                action="syndrome_analysis",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _prescription_handler(self, request):
        """处方接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'pre_' + str(hash(str(data)))),
                agent_type="laoke",
                action="prescription",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _wellness_plan_handler(self, request):
        """养生计划接口处理器"""
        try:
            data = await request.json()
            
            agent_request = AgentRequest(
                request_id=data.get('request_id', 'wel_' + str(hash(str(data)))),
                agent_type="laoke",
                action="wellness_plan",
                input_data=data,
                user_id=data.get('user_id')
            )
            
            response = await self.process_request(agent_request)
            return web.json_response(response.result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def _knowledge_handler(self, request):
        """知识库接口处理器"""
        return web.json_response({
            "agent": "laoke",
            "knowledge_base": self.tcm_knowledge,
            "capabilities": [
                "中医辨证分析",
                "中药处方开具",
                "体质辨识",
                "养生指导",
                "病机分析"
            ],
            "specialties": [
                "内科杂病",
                "体质调理",
                "养生保健",
                "情志调节"
            ]
        })

async def main():
    """主函数"""
    service = LaokeOptimizedService()
    
    port = int(os.getenv("PORT", "8002"))
    host = os.getenv("HOST", "0.0.0.0")
    
    await service.start_server(host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main()) 