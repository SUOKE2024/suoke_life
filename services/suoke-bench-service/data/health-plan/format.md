# HealthPlan-TCM 数据集格式说明

HealthPlan-TCM 数据集是针对不同中医体质人群的个性化健康方案数据集，用于评估智能体生成个性化健康管理方案的能力。

## 数据组织结构

```
health-plan/
├── metadata.json                # 元数据信息
├── constitution/                # 按体质分类的健康方案
│   ├── qi_deficiency/           # 气虚质
│   ├── yang_deficiency/         # 阳虚质
│   ├── yin_deficiency/          # 阴虚质
│   ├── phlegm_dampness/         # 痰湿质
│   ├── damp_heat/               # 湿热质
│   ├── blood_stasis/            # 血瘀质
│   ├── qi_stagnation/           # 气郁质
│   ├── special_constitution/    # 特禀质
│   └── balanced/                # 平和质
├── scenarios/                   # 按场景分类的健康方案
│   ├── daily_life/              # 日常生活
│   ├── work_office/             # 工作办公
│   ├── travel/                  # 旅行
│   ├── sports/                  # 运动健身
│   ├── seasonal/                # 季节变化
│   └── special_periods/         # 特殊时期（如妊娠期）
└── combined/                    # 综合健康方案（体质+场景）
    ├── train/                   # 训练集
    ├── val/                     # 验证集
    └── test/                    # 测试集（用于评测）
```

## 数据格式

健康方案数据采用JSON格式，基本结构如下：

```json
{
  "id": "health_plan_001",
  "title": "气虚体质办公族夏季养生方案",
  "constitution_type": "气虚质",
  "scenario": "work_office",
  "season": "summer",
  "target_population": {
    "age_range": [25, 45],
    "gender": "all",
    "occupation": "office_worker"
  },
  "chief_complaints": ["易疲劳", "多汗", "注意力不集中"],
  "diagnosis": {
    "main_syndromes": ["脾肺气虚"],
    "secondary_syndromes": ["湿热内蕴"],
    "severity": "中度"
  },
  "health_plan": {
    "diet": {
      "principles": ["益气健脾", "清利湿热"],
      "recommended_foods": [
        {
          "name": "山药",
          "amount": "50g",
          "frequency": "daily",
          "cooking_method": "蒸食或煲汤",
          "effect": "健脾益肺，补益中气"
        },
        {
          "name": "莲子",
          "amount": "30g",
          "frequency": "3-4次/周",
          "cooking_method": "煮粥",
          "effect": "补脾止泻，益肾固精"
        }
      ],
      "avoid_foods": [
        {
          "name": "生冷食物",
          "reason": "损伤脾胃"
        },
        {
          "name": "油腻煎炸食物",
          "reason": "增加湿热"
        }
      ],
      "meal_plan": [
        {
          "meal": "早餐",
          "suggestions": "山药小米粥，搭配少量坚果"
        },
        {
          "meal": "午餐",
          "suggestions": "清淡易消化主食，蒸煮蔬菜为主，适量瘦肉"
        },
        {
          "meal": "下午茶",
          "suggestions": "西洋参泡水，搭配少量水果"
        },
        {
          "meal": "晚餐",
          "suggestions": "清淡为主，避免过饱，适量优质蛋白"
        }
      ]
    },
    "exercise": {
      "principles": ["适度锻炼", "避免过度疲劳"],
      "recommended_activities": [
        {
          "name": "太极",
          "duration": "30分钟",
          "frequency": "3次/周",
          "intensity": "低",
          "effect": "调节气息，增强体质",
          "cautions": "动作宜缓不宜猛"
        },
        {
          "name": "步行",
          "duration": "20-30分钟",
          "frequency": "每日",
          "intensity": "低到中",
          "effect": "促进气血运行",
          "cautions": "避免中午高温时段"
        }
      ],
      "avoid_activities": [
        {
          "name": "剧烈有氧运动",
          "reason": "易耗气伤阴"
        },
        {
          "name": "大强度力量训练",
          "reason": "易损伤气血"
        }
      ]
    },
    "living_habits": {
      "principles": ["作息规律", "保持乐观"],
      "recommendations": [
        {
          "category": "睡眠",
          "suggestions": "22:00前入睡，保证7-8小时睡眠，午间可短暂午休15-30分钟"
        },
        {
          "category": "工作环境",
          "suggestions": "保持通风，每工作1小时起身活动5分钟，调整坐姿"
        },
        {
          "category": "情绪管理",
          "suggestions": "练习深呼吸放松，保持心情舒畅，避免暴怒"
        },
        {
          "category": "着装",
          "suggestions": "夏季注意防晒，同时避免过度贪凉，空调温度不宜过低"
        }
      ]
    },
    "herbal_therapy": {
      "principles": ["益气健脾为主"],
      "prescriptions": [
        {
          "name": "四君子汤加减",
          "composition": "人参10g，白术15g，茯苓15g，甘草6g，黄芪15g，山药15g",
          "preparation": "水煎服",
          "dosage": "每日1剂，分2次服用",
          "course": "连服14天为1个疗程",
          "indications": "脾肺气虚，表现为倦怠乏力，气短懒言，自汗等"
        }
      ],
      "health_products": [
        {
          "name": "西洋参片",
          "dosage": "3g",
          "usage": "泡水饮用",
          "frequency": "每日1次",
          "suitable_population": "气虚体质办公室工作者",
          "cautions": "胃热者慎用"
        }
      ]
    },
    "acupoint_stimulation": {
      "principles": ["补气健脾为主"],
      "points": [
        {
          "name": "足三里",
          "location": "外膝眼下3寸",
          "method": "按揉",
          "duration": "3-5分钟",
          "frequency": "每日1-2次",
          "effect": "补中益气，健脾和胃"
        },
        {
          "name": "内关",
          "location": "腕横纹上2寸，两筋之间",
          "method": "按揉",
          "duration": "2-3分钟",
          "frequency": "工作间隙，每日多次",
          "effect": "宁心安神，理气和胃"
        }
      ],
      "massage_techniques": [
        {
          "name": "腹部顺时针按摩",
          "method": "用掌心在腹部做顺时针按摩",
          "duration": "5分钟",
          "frequency": "晚上睡前",
          "effect": "理气健脾",
          "cautions": "力度适中，不可过重"
        }
      ]
    }
  },
  "expected_outcomes": {
    "short_term": ["缓解疲劳感", "改善注意力", "减少多汗"],
    "medium_term": ["提高工作效率", "改善睡眠质量", "增强体质"],
    "long_term": ["脾肺功能增强", "气虚体质改善", "提高免疫力"]
  },
  "follow_up": {
    "frequency": "1次/月",
    "focus_points": ["疲劳程度", "睡眠质量", "消化功能"],
    "adjustment_principles": "根据季节变化及体质改变动态调整方案"
  },
  "expert_notes": "气虚体质在夏季尤其容易出现疲劳加重、多汗等症状，在办公环境中更需注意养护肺脾之气，防止久坐耗气，避免空调直吹损伤卫气"
}
```

## 数据集获取

完整数据集可通过以下命令下载：

```bash
python -m internal.suokebench.setup --download-data health-plan
```

## 引用与来源

HealthPlan-TCM 数据集由索克生活APP团队与中医专家合作收集与标注，用于研究基于中医理论的个性化健康管理方案。 