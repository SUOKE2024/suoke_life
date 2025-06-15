"""
中医微服务客户端

用于调用其他中医相关微服务，获取体质、经络、中药等信息
"""

import aiohttp
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..config.settings import get_settings
from ..core.logging import get_logger


class TCMServiceClient:
    """中医服务客户端"""

    def __init__(self):
        self.settings = get_settings()
        self.logger = get_logger(__name__)
        
        # 中医相关微服务地址配置
        self.tcm_constitution_service_url = getattr(self.settings, 'tcm_constitution_service_url', 'http://localhost:8010')
        self.tcm_meridian_service_url = getattr(self.settings, 'tcm_meridian_service_url', 'http://localhost:8011')
        self.tcm_herbal_service_url = getattr(self.settings, 'tcm_herbal_service_url', 'http://localhost:8012')
        self.unified_health_service_url = getattr(self.settings, 'unified_health_service_url', 'http://localhost:8001')
        
        # 请求超时配置
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def get_user_constitution(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户体质信息"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_constitution_service_url}/api/constitution/user/{user_id}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"成功获取用户 {user_id} 的体质信息")
                        return data
                    elif response.status == 404:
                        self.logger.info(f"用户 {user_id} 暂无体质评估记录")
                        return None
                    else:
                        self.logger.error(f"获取用户体质信息失败: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"调用体质服务失败: {str(e)}")
            return None

    async def get_constitution_recommendations(self, constitution_type: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """获取体质调养建议"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_constitution_service_url}/api/constitution/recommendations"
                payload = {
                    "constitution_type": constitution_type,
                    "user_profile": user_profile,
                    "season": self._get_current_season()
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"成功获取 {constitution_type} 体质调养建议")
                        return data
                    else:
                        self.logger.error(f"获取体质建议失败: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"调用体质建议服务失败: {str(e)}")
            return {}

    async def get_meridian_analysis(self, symptoms: List[str], affected_areas: List[str]) -> Dict[str, Any]:
        """获取经络分析"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_meridian_service_url}/api/meridian/analyze"
                payload = {
                    "symptoms": symptoms,
                    "affected_areas": affected_areas,
                    "analysis_type": "comprehensive"
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info("成功获取经络分析结果")
                        return data
                    else:
                        self.logger.error(f"获取经络分析失败: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"调用经络分析服务失败: {str(e)}")
            return {}

    async def get_acupuncture_points(self, condition: str, constitution_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取针灸穴位建议"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_meridian_service_url}/api/acupuncture/points"
                params = {"condition": condition}
                if constitution_type:
                    params["constitution"] = constitution_type
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"成功获取 {condition} 的穴位建议")
                        return data.get("points", [])
                    else:
                        self.logger.error(f"获取穴位建议失败: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"调用穴位建议服务失败: {str(e)}")
            return []

    async def get_herbal_recommendations(self, symptoms: List[str], constitution_type: Optional[str] = None) -> Dict[str, Any]:
        """获取中药建议"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_herbal_service_url}/api/herbs/recommend"
                payload = {
                    "symptoms": symptoms,
                    "constitution_type": constitution_type,
                    "recommendation_type": "formula"
                }
                
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info("成功获取中药建议")
                        return data
                    else:
                        self.logger.error(f"获取中药建议失败: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"调用中药建议服务失败: {str(e)}")
            return {}

    async def get_seasonal_guidance(self, constitution_type: str, season: Optional[str] = None) -> Dict[str, Any]:
        """获取时令养生指导"""
        try:
            if not season:
                season = self._get_current_season()
                
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.tcm_constitution_service_url}/api/seasonal/guidance"
                params = {
                    "constitution": constitution_type,
                    "season": season
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"成功获取 {season} 季节养生指导")
                        return data
                    else:
                        self.logger.error(f"获取时令养生指导失败: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"调用时令养生服务失败: {str(e)}")
            return {}

    async def get_user_health_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """从统一健康数据服务获取用户健康数据"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.unified_health_service_url}/api/health/user/{user_id}/data"
                params = {"days": days}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"成功获取用户 {user_id} 的健康数据")
                        return data
                    else:
                        self.logger.error(f"获取用户健康数据失败: {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"调用健康数据服务失败: {str(e)}")
            return {}

    async def get_tcm_health_assessment(self, user_id: str) -> Dict[str, Any]:
        """获取中医健康评估"""
        try:
            # 并发获取多个服务的数据
            tasks = [
                self.get_user_constitution(user_id),
                self.get_user_health_data(user_id),
                self.get_seasonal_guidance("", self._get_current_season())
            ]
            
            constitution_data, health_data, seasonal_data = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 整合评估结果
            assessment = {
                "user_id": user_id,
                "assessment_date": datetime.now().isoformat(),
                "constitution": constitution_data if not isinstance(constitution_data, Exception) else None,
                "health_data": health_data if not isinstance(health_data, Exception) else {},
                "seasonal_guidance": seasonal_data if not isinstance(seasonal_data, Exception) else {},
                "integrated_recommendations": []
            }
            
            # 生成整合建议
            if assessment["constitution"] and assessment["health_data"]:
                assessment["integrated_recommendations"] = await self._generate_integrated_recommendations(
                    assessment["constitution"], assessment["health_data"], assessment["seasonal_guidance"]
                )
            
            self.logger.info(f"成功生成用户 {user_id} 的中医健康评估")
            return assessment
            
        except Exception as e:
            self.logger.error(f"生成中医健康评估失败: {str(e)}")
            return {}

    async def search_tcm_knowledge(self, query: str, category: str = "all") -> List[Dict[str, Any]]:
        """搜索中医知识库"""
        try:
            # 根据类别调用不同的服务
            if category == "constitution":
                service_url = self.tcm_constitution_service_url
                endpoint = "/api/knowledge/constitution/search"
            elif category == "meridian":
                service_url = self.tcm_meridian_service_url
                endpoint = "/api/knowledge/meridian/search"
            elif category == "herbs":
                service_url = self.tcm_herbal_service_url
                endpoint = "/api/knowledge/herbs/search"
            else:
                # 搜索所有类别
                tasks = [
                    self._search_service_knowledge(self.tcm_constitution_service_url, "/api/knowledge/constitution/search", query),
                    self._search_service_knowledge(self.tcm_meridian_service_url, "/api/knowledge/meridian/search", query),
                    self._search_service_knowledge(self.tcm_herbal_service_url, "/api/knowledge/herbs/search", query)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                combined_results = []
                for result in results:
                    if not isinstance(result, Exception) and result:
                        combined_results.extend(result)
                
                return combined_results
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{service_url}{endpoint}"
                params = {"query": query, "limit": 10}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        return []
                        
        except Exception as e:
            self.logger.error(f"搜索中医知识库失败: {str(e)}")
            return []

    async def _search_service_knowledge(self, service_url: str, endpoint: str, query: str) -> List[Dict[str, Any]]:
        """搜索单个服务的知识库"""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{service_url}{endpoint}"
                params = {"query": query, "limit": 5}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("results", [])
                    else:
                        return []
        except Exception:
            return []

    async def _generate_integrated_recommendations(self, constitution: Dict[str, Any], 
                                                 health_data: Dict[str, Any], 
                                                 seasonal_data: Dict[str, Any]) -> List[str]:
        """生成整合的中医建议"""
        recommendations = []
        
        try:
            constitution_type = constitution.get("primary_constitution")
            if constitution_type:
                recommendations.append(f"根据您的{constitution_type}体质特点，建议...")
            
            # 基于健康数据的建议
            if health_data.get("recent_symptoms"):
                symptoms = health_data["recent_symptoms"]
                recommendations.append(f"针对您近期的{', '.join(symptoms[:3])}症状，建议...")
            
            # 基于季节的建议
            season = seasonal_data.get("season")
            if season:
                recommendations.append(f"当前{season}季节，建议您...")
            
            # 综合调养建议
            recommendations.extend([
                "保持规律作息，早睡早起",
                "饮食清淡，避免过度油腻",
                "适当运动，如太极拳、八段锦等",
                "保持心情愉悦，避免过度焦虑"
            ])
            
        except Exception as e:
            self.logger.error(f"生成整合建议失败: {str(e)}")
            recommendations = ["建议咨询专业中医师获取个性化指导"]
        
        return recommendations

    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"

    async def health_check(self) -> Dict[str, Any]:
        """检查中医服务连接状态"""
        services = {
            "constitution_service": self.tcm_constitution_service_url,
            "meridian_service": self.tcm_meridian_service_url,
            "herbal_service": self.tcm_herbal_service_url,
            "health_service": self.unified_health_service_url
        }
        
        status = {"tcm_services": {}}
        
        for service_name, service_url in services.items():
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    async with session.get(f"{service_url}/health") as response:
                        status["tcm_services"][service_name] = {
                            "status": "healthy" if response.status == 200 else "unhealthy",
                            "url": service_url,
                            "response_code": response.status
                        }
            except Exception as e:
                status["tcm_services"][service_name] = {
                    "status": "unreachable",
                    "url": service_url,
                    "error": str(e)
                }
        
        return status