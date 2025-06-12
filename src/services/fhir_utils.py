"""
fhir_utils - 索克生活项目模块
"""

import json
from typing import Any, Dict

# -*- coding: utf-8 -*-
"""
FHIR健康数据标准工具
支持健康数据采集、存储、交换的FHIR格式转换与校验
"""

# 以体温采集为例，生成FHIR Observation资源


def to_fhir_observation_temperature(
    user_id: str, value: float, unit: str = "Celsius", effective_time: str = None
) -> Dict[str, Any]:
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8310-5",
                    "display": "Body temperature",
                }
            ]
        },
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": effective_time,
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit,
        },
    }


def to_fhir_observation_blood_pressure(
    user_id: str,
    systolic: float,
    diastolic: float,
    unit: str = "mmHg",
    effective_time: str = None,
):
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel",
                }
            ]
        },
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": effective_time,
        "component": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure",
                        }
                    ]
                },
                "valueQuantity": {
                    "value": systolic,
                    "unit": unit,
                    "system": "http://unitsofmeasure.org",
                    "code": unit,
                },
            },
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic blood pressure",
                        }
                    ]
                },
                "valueQuantity": {
                    "value": diastolic,
                    "unit": unit,
                    "system": "http://unitsofmeasure.org",
                    "code": unit,
                },
            },
        ],
    }


def to_fhir_observation_heart_rate(
    user_id: str, value: float, unit: str = "bpm", effective_time: str = None
):
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8867-4",
                    "display": "Heart rate",
                }
            ]
        },
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": effective_time,
        "valueQuantity": {
            "value": value,
            "unit": unit,
            "system": "http://unitsofmeasure.org",
            "code": unit,
        },
    }


# FHIR Observation校验（简化版）
def validate_fhir_observation(obs: Dict[str, Any]) -> bool:
    required_fields = ["resourceType", "status", "code", "subject", "valueQuantity"]
    return (
        all(field in obs for field in required_fields)
        and obs["resourceType"] == "Observation"
    )


# FHIR Observation转JSON字符串
def fhir_observation_to_json(obs: Dict[str, Any]) -> str:
    return json.dumps(obs, ensure_ascii=False, indent=2)


# 示例用法
def example():
    obs = to_fhir_observation_temperature(
        "user123", 36.7, "Celsius", "2024-05-30T10:00:00+08:00"
    )
    assert validate_fhir_observation(obs)
    print(fhir_observation_to_json(obs))


if __name__ == "__main__":
    example()
