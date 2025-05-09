# 索克生活APP数据模型设计

## 数据模型概述

索克生活APP的数据模型设计遵循领域驱动设计(DDD)原则，将复杂的中医健康管理业务领域模型化。数据模型结构充分考虑了多智能体系统、中医特色功能与现代健康管理的需求，确保数据完整性、关联性和扩展性。

## 核心领域实体

### 用户领域

#### User (用户)

```dart
class User {
  final String id;               // 用户唯一标识
  final String username;         // 用户名
  final String? displayName;     // 显示名称
  final String email;            // 电子邮件
  final String phoneNumber;      // 手机号码
  final String? avatarUrl;       // 头像URL
  final DateTime createdAt;      // 创建时间
  final DateTime lastLoginAt;    // 最后登录时间
  final UserStatus status;       // 用户状态
  final IdentityLevel identityLevel; // 身份认证等级
  final PrivacySettings privacySettings; // 隐私设置
  final List<Role> roles;        // 用户角色列表
  // 其他用户基本属性
}
```

#### HealthProfile (健康档案)

```dart
class HealthProfile {
  final String id;
  final String userId;           // 所属用户ID
  final PersonalInfo personalInfo; // 个人基本信息
  final BodyConstitution bodyConstitution; // 体质信息
  final MedicalHistory medicalHistory; // 病史信息
  final List<HealthExamination> examinations; // 检查记录
  final List<Prescription> prescriptions; // 处方记录
  final List<LifestyleData> lifestyleData; // 生活方式数据
  final DateTime lastUpdatedAt;  // 最后更新时间
  // 其他健康档案属性
}
```

#### BodyConstitution (体质)

```dart
class BodyConstitution {
  final String id;
  final String userId;           // 所属用户ID
  final DateTime assessmentDate; // 评估日期
  final ConstitutionType primaryType; // 主要体质类型
  final Map<ConstitutionType, double> typeScores; // 各体质得分
  final Map<String, dynamic> constitutionFeatures; // 体质特征
  final List<ConstitutionChange> historyChanges; // 历史变化记录
  final String? assessmentSource; // 评估来源(智能体/专业医师)
  // 其他体质相关属性
}

enum ConstitutionType {
  balanced,    // 平和质
  qiDeficient, // 气虚质
  yangDeficient, // 阳虚质
  yinDeficient,  // 阴虚质
  phlegmDamp,   // 痰湿质
  dampHeat,     // 湿热质
  bloodStasis,  // 血瘀质
  qiStagnation, // 气郁质
  specialDiathesis, // 特禀质
}
```

#### Achievement (成就)

```dart
class Achievement {
  final String id;
  final String name;             // 成就名称
  final String description;      // 成就描述
  final String iconUrl;          // 成就图标
  final AchievementCategory category; // 成就类别
  final int experiencePoints;    // 获得的经验值
  final List<Requirement> requirements; // 获得条件
  final Map<String, dynamic> metadata; // 其他元数据
}

class UserAchievement {
  final String id;
  final String userId;           // 用户ID
  final String achievementId;    // 成就ID
  final DateTime unlockedAt;     // 解锁时间
  final int progressPercent;     // 进度百分比(0-100)
  final bool isDisplayed;        // 是否在个人资料中展示
}
```

#### Role (角色)

```dart
class Role {
  final String id;
  final String name;             // 角色名称
  final String description;      // 角色描述
  final String iconUrl;          // 角色图标
  final RoleCategory category;   // 角色类别
  final int requiredLevel;       // 所需等级
  final List<Ability> abilities; // 角色能力
  final Map<String, dynamic> metadata; // 其他元数据
}

class UserRole {
  final String id;
  final String userId;           // 用户ID
  final String roleId;           // 角色ID
  final DateTime assignedAt;     // 获得时间
  final int proficiencyLevel;    // 熟练度等级(1-5)
  final bool isActive;           // 是否当前激活
}
```

### 中医诊断领域

#### FourDiagnosticExamination (四诊记录)

```dart
class FourDiagnosticExamination {
  final String id;
  final String userId;                // 用户ID
  final DateTime examinationTime;     // 检查时间
  final InspectionData? inspectionData; // 望诊数据
  final AuscultationData? auscultationData; // 闻诊数据
  final InquiryData? inquiryData;     // 问诊数据
  final PalpationData? palpationData; // 切诊数据
  final List<DiagnosticConclusion> conclusions; // 诊断结论
  final String? practitionerId;       // 医师ID(如果有)
  final String? aiAgentId;            // AI代理ID(如果是AI辅助诊断)
  final Map<String, dynamic> metadata; // 其他元数据
}
```

#### InspectionData (望诊数据)

```dart
class InspectionData {
  final String id;
  final String examinationId;     // 所属四诊记录ID
  final TongueData? tongueData;   // 舌象数据
  final FacialData? facialData;   // 面色数据
  final BodyPostureData? postureData; // 形体姿态数据
  final List<String> imageUrls;   // 相关图像URL
  final Map<String, dynamic> observations; // 望诊观察结果
}

class TongueData {
  final TongueColor tongueColor;  // 舌色
  final TongueShape tongueShape;  // 舌形
  final TongueCoating coatingType; // 苔质
  final TongueCoatingColor coatingColor; // 苔色
  final TongueMoisture moisture;  // 舌润燥
  final Map<String, double> featureConfidence; // 特征识别置信度
  final Map<String, dynamic> additionalFeatures; // 其他特征
}
```

#### AuscultationData (闻诊数据)

```dart
class AuscultationData {
  final String id;
  final String examinationId;     // 所属四诊记录ID
  final VoiceData? voiceData;     // 语音数据
  final BreathData? breathData;   // 呼吸数据
  final List<String> audioUrls;   // 相关音频URL
  final Map<String, dynamic> observations; // 闻诊观察结果
}
```

#### InquiryData (问诊数据)

```dart
class InquiryData {
  final String id;
  final String examinationId;     // 所属四诊记录ID
  final Map<String, dynamic> chiefComplaints; // 主诉
  final Map<String, dynamic> systemReview;    // 系统回顾
  final Map<String, dynamic> lifestyleFactors; // 生活方式因素
  final Map<String, dynamic> emotionalStatus;  // 情志状态
  final String conversationSummary;           // 对话摘要
  final Map<String, dynamic> observations;     // 问诊观察结果
}
```

#### PalpationData (切诊数据)

```dart
class PalpationData {
  final String id;
  final String examinationId;     // 所属四诊记录ID
  final PulseData? pulseData;     // 脉象数据
  final AbdomenData? abdomenData; // 腹诊数据
  final Map<String, dynamic> acupointReactions; // 穴位反应
  final Map<String, dynamic> observations; // 切诊观察结果
}

class PulseData {
  final PulseDepth depth;         // 脉位(浮沉)
  final PulseRate rate;           // 脉率(迟数)
  final PulseStrength strength;   // 脉力(虚实)
  final PulseRhythm rhythm;       // 脉律(结代)
  final PulseWidth width;         // 脉幅(洪细)
  final Map<String, dynamic> waveformData; // 脉波数据
  final Map<String, dynamic> additionalFeatures; // 其他特征
}
```

#### DiagnosticConclusion (诊断结论)

```dart
class DiagnosticConclusion {
  final String id;
  final String examinationId;     // 所属四诊记录ID
  final List<ConstitutionType> constitutionAssessment; // 体质评估
  final List<PatternDifferentiation> patternDifferentiation; // 辨证
  final List<String> healthSuggestions; // 养生建议
  final double confidenceLevel;   // 结论置信度(0.0-1.0)
  final DiagnosticSource source;  // 结论来源(医师/AI)
  final DateTime concludedAt;     // 结论时间
}
```

### 医疗服务领域

#### Practitioner (医师)

```dart
class Practitioner {
  final String id;
  final String name;             // 姓名
  final String title;            // 职称
  final String? avatarUrl;       // 头像URL
  final String? biography;       // 个人简介
  final List<MedicalSpecialty> specialties; // 专长领域
  final List<Qualification> qualifications; // 资质认证
  final List<WorkingHours> availability; // 出诊时间
  final double rating;           // 评分(1-5)
  final int consultationCount;   // 问诊次数
  final List<PractitionerRating> ratings; // 评价记录
  final Map<String, dynamic> metadata; // 其他元数据
}
```

#### Appointment (预约)

```dart
class Appointment {
  final String id;
  final String userId;           // 用户ID
  final String practitionerId;   // 医师ID
  final DateTime appointmentTime; // 预约时间
  final Duration duration;       // 预约时长
  final AppointmentType type;    // 预约类型(线上/线下)
  final AppointmentStatus status; // 预约状态
  final String? locationId;      // 地点ID(线下预约)
  final PaymentInfo? paymentInfo; // 支付信息
  final String? notes;           // 备注
  final DateTime createdAt;      // 创建时间
  final DateTime updatedAt;      // 更新时间
}
```

#### Prescription (处方)

```dart
class Prescription {
  final String id;
  final String userId;           // 用户ID
  final String? practitionerId;  // 医师ID
  final String? aiAgentId;       // AI代理ID(如为AI辅助)
  final DateTime prescribedAt;   // 开具时间
  final List<Medication> medications; // 药物列表
  final List<HerbalFormulation> herbalFormulations; // 中药方剂
  final String diagnosticSummary; // 诊断摘要
  final String instructions;     // 用药说明
  final PrescriptionValidity validity; // 有效期
  final PrescriptionStatus status; // 处方状态
}

class HerbalFormulation {
  final String id;
  final String name;             // 方剂名称
  final String? classicalReference; // 经典出处
  final List<HerbalComponent> components; // 组成药材
  final String preparationMethod; // 煎煮方法
  final String administrationMethod; // 服用方法
  final String? modifications;   // 加减说明
}
```

### 食农结合领域

#### Recipe (食谱)

```dart
class Recipe {
  final String id;
  final String name;             // 食谱名称
  final String description;      // 描述
  final List<String> imageUrls;  // 图片URL
  final List<Ingredient> ingredients; // 食材列表
  final String instructions;     // 制作步骤
  final List<ConstitutionType> suitableConstitutions; // 适宜体质
  final List<ConstitutionType> unsuitableConstitutions; // 不宜体质
  final List<HealthBenefit> healthBenefits; // 健康功效
  final SeasonalRecommendation seasonality; // 时令推荐
  final String? creatorId;       // 创建者ID
  final RecipeCategory category; // 食谱分类
  final double difficulty;       // 难度(1-5)
  final Duration preparationTime; // 准备时间
  final int servings;            // 份量
  final List<String> tags;       // 标签
}
```

#### Ingredient (食材)

```dart
class Ingredient {
  final String id;
  final String name;             // 食材名称
  final String? imageUrl;        // 图片URL
  final IngredientCategory category; // 食材分类
  final List<NutritionalValue> nutritionalValues; // 营养价值
  final List<MedicinalProperty> medicinalProperties; // 药性属性
  final List<ConstitutionType> suitableConstitutions; // 适宜体质
  final List<ConstitutionType> unsuitsableConstitutions; // 不宜体质
  final SeasonalRecommendation seasonality; // 时令性
  final List<StorageMethod> storageMethods; // 存储方法
  final List<String> substitutes; // 替代品
}

class MedicinalProperty {
  final String property;        // 属性名称(如四气五味)
  final String value;           // 属性值
  final String? description;    // 描述说明
}
```

#### FarmProduct (农产品)

```dart
class FarmProduct {
  final String id;
  final String name;             // 产品名称
  final String description;      // 描述
  final String? imageUrl;        // 图片URL
  final double price;            // 价格
  final Farm farm;               // 生产农场
  final List<Certification> certifications; // 认证
  final ProductionMethod productionMethod; // 生产方式
  final SeasonalAvailability availability; // 供应季节
  final Map<String, String> traceabilityInfo; // 溯源信息
  final List<IngredientId> relatedIngredients; // 相关食材
  final List<String> tags;       // 标签
}
```

#### Farm (农场)

```dart
class Farm {
  final String id;
  final String name;             // 农场名称
  final String? description;     // 农场描述
  final String? imageUrl;        // 图片URL
  final Location location;       // 位置
  final String contactInfo;      // 联系方式
  final List<Certification> certifications; // 认证
  final List<FarmingMethod> farmingMethods; // 种植方法
  final double rating;           // 评分(1-5)
  final List<String> specialties; // 特色产品
  final List<FarmActivity> activities; // 农事活动
}
```

#### FarmActivity (农事活动)

```dart
class FarmActivity {
  final String id;
  final String name;             // 活动名称
  final String description;      // 活动描述
  final String? imageUrl;        // 图片URL
  final Farm farm;               // 主办农场
  final DateTime startTime;      // 开始时间
  final DateTime endTime;        // 结束时间
  final int capacity;            // 容量
  final double price;            // 价格
  final ActivityCategory category; // 活动类别
  final SeasonalContext seasonalContext; // 节气背景
  final List<String> highlights; // 活动亮点
  final List<String> requirements; // 参与要求
  final ActivityStatus status;   // 活动状态
}
```

### 山水养生领域

#### WellnessDestination (养生胜地)

```dart
class WellnessDestination {
  final String id;
  final String name;             // 名称
  final String description;      // 描述
  final List<String> imageUrls;  // 图片URL
  final Location location;       // 位置
  final List<DestinationFeature> features; // 特色
  final ClimateInfo climateInfo; // 气候信息
  final List<ConstitutionType> suitableConstitutions; // 适宜体质
  final Map<Season, double> seasonalRatings; // 季节适宜度
  final List<NaturalResource> naturalResources; // 自然资源
  final List<WellnessActivity> activities; // 养生活动
  final int popularityRank;      // 受欢迎程度排名
  final double rating;           // 评分(1-5)
}
```

#### NaturalTherapy (自然疗法)

```dart
class NaturalTherapy {
  final String id;
  final String name;             // 疗法名称
  final String description;      // 描述
  final String? imageUrl;        // 图片URL
  final TherapyCategory category; // 疗法类别
  final List<TherapyEffect> effects; // 疗效
  final List<ConstitutionType> suitableConstitutions; // 适宜体质
  final List<ConstitutionType> unsuitsableConstitutions; // 不宜体质
  final List<PracticeMethod> practiceMethods; // 实践方法
  final List<String> scientificReferences; // 科学依据
  final List<WellnessDestination> recommendedLocations; // 推荐地点
}
```

### AI智能体领域

#### AIAgent (智能体)

```dart
class AIAgent {
  final String id;
  final String name;             // 名称
  final AgentType type;          // 类型(小艾/小克/老克/索儿)
  final String description;      // 描述
  final String? avatarUrl;       // 头像URL
  final List<AgentCapability> capabilities; // 能力列表
  final AgentStatus status;      // 状态
  final AgentPersonality personality; // 性格特征
  final AgentMemory memory;      // 记忆系统
  final Map<String, dynamic> configuration; // 配置信息
  final DateTime lastUpdatedAt;  // 最后更新时间
  final String modelVersion;     // 模型版本
}
```

#### Conversation (对话)

```dart
class Conversation {
  final String id;
  final String userId;           // 用户ID
  final List<String> participantAgentIds; // 参与智能体ID
  final DateTime startTime;      // 开始时间
  final DateTime? endTime;       // 结束时间
  final ConversationStatus status; // 对话状态
  final String? title;           // 对话标题(可自动生成)
  final List<Message> messages;  // 消息列表
  final Map<String, dynamic> metadata; // 元数据(如相关模块、标签等)
}

class Message {
  final String id;
  final String conversationId;   // 对话ID
  final String senderId;         // 发送者ID(用户或AI)
  final SenderType senderType;   // 发送者类型(用户/AI)
  final DateTime timestamp;      // 时间戳
  final MessageType type;        // 消息类型
  final String content;          // 文本内容
  final List<MediaAttachment>? attachments; // 媒体附件
  final Map<String, dynamic>? metadata; // 元数据
}
```

#### AgentTask (智能体任务)

```dart
class AgentTask {
  final String id;
  final String agentId;          // 智能体ID
  final String? userId;          // 相关用户ID
  final String title;            // 任务标题
  final String description;      // 任务描述
  final TaskType type;           // 任务类型
  final TaskPriority priority;   // 优先级
  final TaskStatus status;       // 状态
  final DateTime createdAt;      // 创建时间
  final DateTime? completedAt;   // 完成时间
  final List<TaskStep> steps;    // 任务步骤
  final Map<String, dynamic> parameters; // 任务参数
  final Map<String, dynamic> results;    // 任务结果
}
```

### 知识库领域

#### KnowledgeArticle (知识文章)

```dart
class KnowledgeArticle {
  final String id;
  final String title;            // 标题
  final String content;          // 内容
  final String? thumbnailUrl;    // 缩略图URL
  final List<String> tags;       // 标签
  final KnowledgeCategory category; // 分类
  final String? authorId;        // 作者ID
  final AuthorType authorType;   // 作者类型(用户/AI)
  final DateTime publishedAt;    // 发布时间
  final DateTime? updatedAt;     // 更新时间
  final int viewCount;           // 查看次数
  final int likeCount;           // 点赞次数
  final List<String> relatedArticleIds; // 相关文章
  final List<String> references; // 参考资料
}
```

#### Course (课程)

```dart
class Course {
  final String id;
  final String title;            // 标题
  final String description;      // 描述
  final String? thumbnailUrl;    // 缩略图URL
  final CourseCategory category; // 分类
  final List<CourseModule> modules; // 模块
  final String? instructorId;    // 讲师ID
  final InstructorType instructorType; // 讲师类型(用户/AI)
  final DifficultyLevel difficulty; // 难度
  final Duration estimatedDuration; // 预计时长
  final List<String> prerequisites; // 先决条件
  final List<String> learningOutcomes; // 学习成果
  final int enrollmentCount;     // 报名人数
  final double rating;           // 评分(1-5)
}

class CourseModule {
  final String id;
  final String title;            // 标题
  final String description;      // 描述
  final int sequenceNumber;      // 序号
  final List<LessonUnit> lessons; // 课时
  final List<Quiz> quizzes;      // 测验
  final List<Assignment> assignments; // 作业
}
```

## 数据关系图

```
User ────┬──> HealthProfile ───> BodyConstitution
         ├──> UserAchievement <──── Achievement
         ├──> UserRole <────────── Role
         ├──> Conversation <────── AIAgent
         └──> Appointment ────────> Practitioner
                   │
                   └──> FourDiagnosticExamination
                             │
                             ├──> InspectionData
                             ├──> AuscultationData
                             ├──> InquiryData
                             ├──> PalpationData
                             └──> DiagnosticConclusion
                                       │
                                       └──> Prescription ───> HerbalFormulation ───> Ingredient
                                                                                         │
                                       ┌────────────────────────────────────────────────┘
                                       │
Recipe <─────────┬─────────────────────┘
    │            │                      
    │            └──> FarmProduct <──── Farm ───> FarmActivity
    │                                                    
    └──────────────> WellnessDestination ───> NaturalTherapy

KnowledgeArticle                     Course
       │                                │
       └───────> AIAgent <─────────────┘
                    │
                    └───> AgentTask
```

## 数据存储策略

### 本地存储

1. **SQLite数据库**
   - 用户基本信息
   - 健康档案缓存
   - 对话历史
   - 本地收藏内容
   - 应用设置

2. **安全存储 (flutter_secure_storage)**
   - 认证令牌
   - 加密密钥
   - 敏感用户数据

3. **本地文件系统**
   - 临时媒体文件
   - 缓存图像
   - 离线内容

### 远程存储

1. **关系型数据库 (MySQL/PostgreSQL)**
   - 用户账户信息
   - 健康档案基础数据
   - 预约和交易记录
   - 结构化医疗数据

2. **文档数据库 (MongoDB)**
   - 诊断记录
   - 对话历史
   - 个性化配置
   - 非结构化健康日志

3. **向量数据库 (Milvus/Pinecone)**
   - 医学知识向量
   - 诊断数据向量
   - 用户行为向量
   - 舌象图片特征向量

4. **图数据库 (Neo4j)**
   - 中医知识图谱
   - 用户关系网络
   - 体质-症状-方剂关系
   - 食材药性网络

5. **时序数据库 (InfluxDB)**
   - 健康监测数据
   - 传感器数据流
   - 趋势分析数据
   - 体质变化跟踪

6. **缓存 (Redis)**
   - 会话状态
   - 临时计算结果
   - 热点数据缓存
   - 限流计数器

### 数据同步策略

1. **增量同步**
   - 使用时间戳和版本控制
   - 仅同步变更数据
   - 支持离线操作

2. **冲突解决**
   - 基于应用逻辑的合并策略
   - 冲突标记和人工解决选项
   - 最后写入优先(适用部分数据)

3. **周期性同步**
   - 关键数据实时同步
   - 非关键数据周期同步
   - 后台同步与省电模式

## 数据安全与隐私

### 数据分级保护

1. **公开数据** (Level 1)
   - 通用知识内容
   - 公共健康信息
   - 匿名统计数据

2. **基本个人数据** (Level 2)
   - 用户资料
   - 偏好设置
   - 非敏感互动记录

3. **敏感个人数据** (Level 3)
   - 健康记录摘要
   - 预约历史
   - 支付信息

4. **高度敏感数据** (Level 4)
   - 完整健康档案
   - 诊断结果
   - 医疗影像

5. **临床数据** (Level 5)
   - 原始四诊数据
   - 处方详情
   - 完整病史

### 安全措施

1. **存储安全**
   - 敏感数据加密存储
   - 数据分片与访问控制
   - 安全密钥管理

2. **传输安全**
   - 全程TLS/SSL加密
   - 证书固定防中间人攻击
   - API签名验证

3. **访问控制**
   - 基于角色的访问控制(RBAC)
   - 细粒度权限管理
   - 访问审计日志

4. **数据生命周期**
   - 自动数据老化策略
   - 明确的数据保留期
   - 安全数据销毁流程

## 数据迁移与版本控制

1. **数据库迁移策略**
   - 使用数据库迁移工具
   - 向前兼容原则
   - 迁移回滚计划

2. **模型版本控制**
   - 语义化版本号
   - 模型兼容性保障
   - 渐进式数据模型更新

3. **旧版数据迁移**
   - 自动迁移逻辑
   - 数据转换适配器
   - 迁移完整性校验

## 数据迁移与版本控制

1. **数据库迁移策略**
   - 使用数据库迁移工具
   - 向前兼容原则
   - 迁移回滚计划

2. **模型版本控制**
   - 语义化版本号
   - 模型兼容性保障
   - 渐进式数据模型更新

3. **旧版数据迁移**
   - 自动迁移逻辑
   - 数据转换适配器
   - 迁移完整性校验

## 区块链数据集成

1. **健康数据确权**
   - 使用ERC-1155标准NFT
   - 健康证明零知识验证
   - 数据权属与授权管理

2. **IPFS分布式存储**
   - 健康报告永久存储
   - 内容寻址和去中心化访问
   - 加密内容哈希保护

3. **智能合约集成**
   - 数据访问控制合约
   - 健康激励通证合约
   - 预约与交易合约

## 数据分析与AI训练

1. **匿名化处理流程**
   - 个人标识符移除
   - 分布式差分隐私
   - K-匿名性保障

2. **训练数据管理**
   - 数据集版本控制
   - 数据质量标记
   - 偏见检测与缓解

3. **特征提取管道**
   - 多模态特征标准化
   - 中医特征工程流程
   - 时序特征提取方法

## 多端数据一致性

1. **离线优先设计**
   - 本地优先操作
   - 后台同步机制
   - 连接恢复处理

2. **设备间同步**
   - 基于云的状态同步
   - 增量更新策略
   - 冲突检测与解决

3. **多用户同步**
   - 共享资源锁机制
   - 乐观并发控制
   - 更改通知系统