"""
中医辨证算法模块
提供中医理论的数字化实现和辨证论治算法
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TCMAlgorithm:
    """中医辨证算法类"""

    def __init__(self):
        self.syndrome_patterns = {
            "气虚证": {
                "symptoms": ["乏力", "气短", "懒言", "自汗"],
                "tongue": ["淡白", "薄白苔"],
                "pulse": ["虚弱", "缓慢"],
                "confidence": 0.8
            },
            "血瘀证": {
                "symptoms": ["疼痛", "固定不移", "面色晦暗"],
                "tongue": ["紫暗", "瘀斑"],
                "pulse": ["涩脉", "结代"],
                "confidence": 0.85
            },
            "湿热证": {
                "symptoms": ["身重", "困倦", "口苦", "小便黄"],
                "tongue": ["红", "黄腻苔"],
                "pulse": ["滑数", "濡数"],
                "confidence": 0.82
            }
        }

    def analyze_syndrome(self, symptoms: list[str], tongue_features: dict[str, Any], pulse_features: dict[str, Any]) -> dict[str, Any]:
        """分析证候"""
        try:
            results = []

            for syndrome, pattern in self.syndrome_patterns.items():
                score = self._calculate_syndrome_score(symptoms, tongue_features, pulse_features, pattern)
                if score > 0.5:
                    results.append({
                        "syndrome": syndrome,
                        "score": score,
                        "confidence": pattern["confidence"] * score
                    })

            # 按得分排序
            results.sort(key=lambda x: x["score"], reverse=True)

            return {
                "primary_syndrome": results[0] if results else None,
                "all_syndromes": results,
                "analysis_method": "pattern_matching"
            }

        except Exception as e:
            logger.error(f"证候分析失败: {e}")
            return {"error": "证候分析失败", "details": str(e)}

    def _calculate_syndrome_score(self, symptoms: list[str], tongue_features: dict[str, Any], pulse_features: dict[str, Any], pattern: dict[str, Any]) -> float:
        """计算证候匹配得分"""
        total_score = 0.0
        total_weight = 0.0

        # 症状匹配 (权重: 0.5)
        symptom_score = self._match_symptoms(symptoms, pattern.get("symptoms", []))
        total_score += symptom_score * 0.5
        total_weight += 0.5

        # 舌象匹配 (权重: 0.3)
        tongue_score = self._match_tongue(tongue_features, pattern.get("tongue", []))
        total_score += tongue_score * 0.3
        total_weight += 0.3

        # 脉象匹配 (权重: 0.2)
        pulse_score = self._match_pulse(pulse_features, pattern.get("pulse", []))
        total_score += pulse_score * 0.2
        total_weight += 0.2

        return total_score / total_weight if total_weight > 0 else 0.0

    def _match_symptoms(self, symptoms: list[str], pattern_symptoms: list[str]) -> float:
        """匹配症状"""
        if not pattern_symptoms:
            return 0.0

        matches = sum(1 for symptom in symptoms if any(ps in symptom for ps in pattern_symptoms))
        return matches / len(pattern_symptoms)

    def _match_tongue(self, tongue_features: dict[str, Any], pattern_tongue: list[str]) -> float:
        """匹配舌象"""
        if not pattern_tongue:
            return 0.0

        tongue_desc = f"{tongue_features.get('color', '')} {tongue_features.get('coating', '')}"
        matches = sum(1 for pt in pattern_tongue if pt in tongue_desc)
        return matches / len(pattern_tongue)

    def _match_pulse(self, pulse_features: dict[str, Any], pattern_pulse: list[str]) -> float:
        """匹配脉象"""
        if not pattern_pulse:
            return 0.0

        pulse_desc = pulse_features.get("type", "")
        matches = sum(1 for pp in pattern_pulse if pp in pulse_desc)
        return matches / len(pattern_pulse)


# 全局实例
_tcm_algorithm = None


def get_tcm_algorithm() -> TCMAlgorithm:
    """获取中医算法实例"""
    global _tcm_algorithm
    if _tcm_algorithm is None:
        _tcm_algorithm = TCMAlgorithm()
    return _tcm_algorithm
