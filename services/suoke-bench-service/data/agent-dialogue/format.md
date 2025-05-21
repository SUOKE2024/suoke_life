# SuokeDialogue 数据集格式说明

SuokeDialogue 是索克生活APP四大智能体（小艾、小克、老克、索儿）的协作对话数据集，用于评估多智能体协同决策和问诊能力。

## 数据组织结构

```
agent-dialogue/
├── metadata.json                # 元数据信息
├── single_agent/                # 单智能体对话
│   ├── xiaoai/                  # 小艾（中医四诊）
│   ├── xiaoke/                  # 小克（中医药膳）
│   ├── laoke/                   # 老克（生活养生）
│   └── suoer/                   # 索儿（运动康复）
├── multi_agent/                 # 多智能体协作对话
│   ├── diagnosis/               # 协同问诊场景
│   ├── treatment/               # 协同治疗方案场景
│   ├── daily_guidance/          # 日常生活指导场景
│   └── emergency/               # 紧急情况处理场景
└── annotated/                   # 带专家标注的对话
    ├── train/                   # 训练集
    ├── val/                     # 验证集
    └── test/                    # 测试集（用于评测）
```

## 数据格式

智能体对话数据采用JSON格式，基本结构如下：

```json
{
  "dialogue_id": "dialog_001",
  "title": "中老年气虚体质患者的综合健康管理",
  "scenario": "health_management",
  "timestamp": "2023-08-10T14:30:00Z",
  "user_profile": {
    "age": 58,
    "gender": "female",
    "constitution": "气虚质",
    "health_conditions": ["高血压", "睡眠不佳"],
    "medications": ["降压药"]
  },
  "context": {
    "location": "家庭",
    "time_of_day": "下午",
    "season": "夏季",
    "environmental_factors": ["高温", "空调环境"]
  },
  "dialogue": [
    {
      "turn": 1,
      "speaker": "user",
      "utterance": "最近总是觉得很累，特别是下午，不知道是怎么回事。",
      "modality": "text",
      "timestamp": "2023-08-10T14:30:00Z"
    },
    {
      "turn": 2,
      "speaker": "xiaoai",
      "utterance": "您好！我是小艾，听您说最近容易疲劳，特别是下午比较明显。能否请您详细描述一下，除了疲劳还有其他不适感吗？比如出汗情况、胃口、睡眠质量等？",
      "reasoning": "用户主诉疲劳，需要进一步收集信息，符合气虚体质特征，需要询问其他相关症状。",
      "role": "问诊收集信息",
      "timestamp": "2023-08-10T14:30:15Z"
    },
    {
      "turn": 3,
      "speaker": "user",
      "utterance": "嗯，我确实容易出汗，而且胃口也不太好，饭量比以前小了。晚上睡觉容易醒，有时候还会心慌。",
      "modality": "text",
      "timestamp": "2023-08-10T14:30:45Z"
    },
    {
      "turn": 4,
      "speaker": "xiaoai",
      "utterance": "了解了，您的症状包括疲劳、多汗、胃口差、睡眠不佳和心慌。请您上传一张舌照，我帮您进一步分析。",
      "reasoning": "症状符合气虚特征，需要结合舌象等客观信息进行辨证。",
      "role": "引导提供检查信息",
      "timestamp": "2023-08-10T14:31:15Z"
    },
    {
      "turn": 5,
      "speaker": "user",
      "utterance": "[舌像图片]",
      "modality": "image",
      "media_url": "tongue_images/dialog_001_tongue.jpg",
      "timestamp": "2023-08-10T14:31:45Z"
    },
    {
      "turn": 6,
      "speaker": "xiaoai",
      "utterance": "根据您的舌象和症状，您目前表现为气虚兼有心血不足的状态。我建议邀请小克和老克一起为您提供综合建议，您觉得如何？",
      "reasoning": "舌体胖大、边有齿痕、舌质淡红、舌苔薄白，结合症状判断为气虚，兼有心血不足。需要饮食调养和生活方式调整，应邀请相关专长的智能体协作。",
      "role": "辨证分析并协调其他智能体",
      "timestamp": "2023-08-10T14:32:15Z",
      "tongue_diagnosis": {
        "tongue_body": "胖大有齿痕",
        "tongue_color": "淡红",
        "tongue_coating": "薄白",
        "diagnosis": "气虚，兼有心血不足"
      }
    },
    {
      "turn": 7,
      "speaker": "system",
      "utterance": "正在邀请小克和老克加入对话...",
      "timestamp": "2023-08-10T14:32:20Z"
    },
    {
      "turn": 8,
      "speaker": "xiaoke",
      "utterance": "您好！我是小克，擅长中医药膳。小艾已经与我分享了您的情况。针对您气虚兼有心血不足的状态，我想为您推荐一些适合的食疗方案。",
      "reasoning": "需要设计针对气虚体质且适合夏季的药膳方案，同时考虑用户有高血压的情况，避免使用升压食材。",
      "role": "药膳规划",
      "timestamp": "2023-08-10T14:32:45Z"
    },
    {
      "turn": 9,
      "speaker": "user",
      "utterance": "好的，我想知道日常应该吃什么好。",
      "modality": "text",
      "timestamp": "2023-08-10T14:33:15Z"
    },
    {
      "turn": 10,
      "speaker": "xiaoke",
      "utterance": "针对您的情况，我建议：\n1. 主食：可以选择小米、糙米、燕麦等全谷物，搭配山药、莲子等制作粥品\n2. 蛋白质：多吃瘦肉、鸡肉、鱼肉，每周吃2-3次鸡蛋\n3. 蔬果：西洋参枸杞炖雪梨是很好的选择，能养阴益气\n4. 汤品：推荐黄芪党参鸡汤，每周可以喝1-2次\n5. 避免辛辣刺激、生冷和油腻食物\n您有高血压，所以请控制盐分摄入。",
      "reasoning": "设计食谱需兼顾补气、养心血和降压需求，选择山药、莲子补气健脾，西洋参、枸杞养心安神，控制盐分以管理高血压。",
      "role": "提供具体饮食指导",
      "timestamp": "2023-08-10T14:33:45Z",
      "food_therapy": {
        "principles": ["益气健脾", "养心安神", "清淡易消化"],
        "key_foods": ["山药", "莲子", "西洋参", "枸杞"],
        "recipes": ["黄芪党参鸡汤", "西洋参枸杞炖雪梨"]
      }
    },
    {
      "turn": 11,
      "speaker": "laoke",
      "utterance": "您好！我是老克，看了您的情况后，想给您一些生活方面的建议：\n1. 作息：尽量在22点前入睡，保证7-8小时睡眠\n2. 环境：夏季注意温差变化，不要长时间待在空调房中\n3. 活动：下午疲劳时可以按摩足三里和内关穴位，每天坚持5分钟\n4. 情绪：保持心情舒畅，可以尝试每天15分钟的冥想\n5. 午休：建议午饭后休息20-30分钟，但不要躺着睡\n这些习惯坚持下来，会逐渐改善您的气虚状态。",
      "reasoning": "气虚体质患者需要规律作息和保持良好精神状态，避免过度劳累；同时考虑夏季气温高、用户使用空调的情况，提醒注意温差变化避免损伤阳气。",
      "role": "生活方式指导",
      "timestamp": "2023-08-10T14:34:15Z",
      "lifestyle_advice": {
        "sleep": "22点前入睡，保证7-8小时",
        "environment": "避免长时间待在空调房",
        "activities": "按摩足三里和内关穴位",
        "emotional": "保持心情舒畅，每天15分钟冥想",
        "rest": "午饭后休息20-30分钟"
      }
    },
    {
      "turn": 12,
      "speaker": "user",
      "utterance": "这些建议很详细，谢谢。我平时还能做什么运动吗？",
      "modality": "text",
      "timestamp": "2023-08-10T14:34:45Z"
    },
    {
      "turn": 13,
      "speaker": "system",
      "utterance": "正在邀请索儿加入对话...",
      "timestamp": "2023-08-10T14:34:50Z"
    },
    {
      "turn": 14,
      "speaker": "suoer",
      "utterance": "您好！我是索儿，很高兴能为您提供运动建议。考虑到您的气虚体质和高血压情况，我建议选择低强度、缓和的运动：\n1. 太极：每天早晨可以练习15-20分钟，加强气血运行\n2. 散步：晚饭后慢走20-30分钟，避开中午高温时段\n3. 八段锦：简单易学，尤其适合气虚体质，每天可以练习一次\n4. 呼吸练习：每天早晚各5分钟腹式呼吸，帮助稳定血压\n请记住，运动时如感到明显疲劳或不适，应立即停止并休息。",
      "reasoning": "气虚体质需避免高强度运动，选择能养气的太极、八段锦等传统运动；同时考虑高血压情况，避免可能导致血压波动的剧烈活动；夏季建议避开高温时段。",
      "role": "运动指导",
      "timestamp": "2023-08-10T14:35:15Z",
      "exercise_plan": {
        "principles": ["低强度", "缓和节奏", "养气为主"],
        "recommended": ["太极", "散步", "八段锦", "腹式呼吸"],
        "frequency": "每天1次，每次15-30分钟",
        "cautions": "感到明显疲劳应立即停止"
      }
    },
    {
      "turn": 15,
      "speaker": "xiaoai",
      "utterance": "总结一下我们四位智能体的建议：您的主要问题是气虚兼有心血不足，加上高血压基础疾病。我们推荐您从饮食、生活习惯和适当运动三方面进行调理。建议您先尝试两周，之后我们可以根据您的反馈调整方案。您有什么疑问吗？",
      "reasoning": "作为引导智能体，需要总结其他智能体的意见，形成完整的健康管理方案，并设定后续随访计划。",
      "role": "总结和协调",
      "timestamp": "2023-08-10T14:35:45Z"
    },
    {
      "turn": 16,
      "speaker": "user",
      "utterance": "没问题，我会按照你们的建议尝试。两周后我再来反馈情况。",
      "modality": "text",
      "timestamp": "2023-08-10T14:36:15Z"
    }
  ],
  "expert_annotation": {
    "annotator": "张医师",
    "overall_quality": 4.5,
    "diagnosis_accuracy": 4.7,
    "recommendations_appropriateness": 4.5,
    "collaboration_efficiency": 4.6,
    "patient_communication": 4.4,
    "comments": "智能体间协作良好，诊断准确，建议全面且符合患者具体情况。可进一步加强对高血压用药与食疗、运动的相互影响分析。"
  },
  "metrics": {
    "response_time": {
      "average": 25.3,
      "max": 35.2,
      "min": 15.1,
      "unit": "seconds"
    },
    "turn_distribution": {
      "xiaoai": 0.25,
      "xiaoke": 0.125,
      "laoke": 0.125,
      "suoer": 0.125,
      "user": 0.375
    },
    "knowledge_coverage": {
      "tcm_diagnosis": 0.9,
      "dietetics": 0.85,
      "lifestyle": 0.8,
      "exercise": 0.85
    }
  }
}
```

## 多智能体协作模式

SuokeDialogue 数据集记录了四种主要协作模式：

1. **诊断协作模式**：以小艾为主导，集成四诊信息，邀请其他智能体提供辅助诊断信息
2. **治疗协作模式**：根据诊断结果，智能体共同制定综合治疗和健康管理方案
3. **顺序协作模式**：智能体按预定顺序接力提供服务，每个智能体专注各自领域
4. **动态协作模式**：根据对话内容实时调整参与的智能体组合

## 数据集获取

完整数据集可通过以下命令下载：

```bash
python -m internal.suokebench.setup --download-data agent-dialogue
```

## 引用与来源

SuokeDialogue 数据集由索克生活APP团队模拟真实用户与智能体的对话场景构建，并邀请中医专家进行标注与评估，用于研究多智能体协作的健康咨询系统。 