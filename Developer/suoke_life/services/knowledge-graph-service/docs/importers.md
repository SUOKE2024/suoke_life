# 知识图谱导入工具使用指南

知识图谱导入工具用于将多种格式的结构化数据导入到知识图谱中，支持中药、方剂等多种数据类型的导入，并能够自动创建节点和关系。本文档提供了各种导入器的详细使用说明和示例。

## 导入器概览

导入工具支持以下数据类型：

| 数据类型 | 导入器 | 说明 |
|---------|-------|------|
| 中药 | HerbImporter | 导入中药数据，创建中药节点及相关关系 |
| 方剂 | FormulaImporter | 导入方剂数据，创建方剂节点及与中药的关系 |

每个导入器都支持多种数据格式，包括CSV、JSON和XML，详细的解析器使用方法请参考[解析器使用指南](parsers.md)。

## 命令行使用

知识图谱导入工具提供了命令行接口，可通过以下命令使用：

```bash
# 导入中药数据
go run cmd/importer/main.go -source data/herbs.csv -type herbs

# 导入方剂数据
go run cmd/importer/main.go -source data/formulas.json -type formulas

# 指定数据格式（自动检测、csv、json、xml）
go run cmd/importer/main.go -source data/herbs.csv -type herbs -format csv

# 仅测试运行，不写入数据库
go run cmd/importer/main.go -source data/herbs.csv -type herbs -dry-run

# 设置日志级别和输出格式
go run cmd/importer/main.go -source data/herbs.csv -type herbs -log-level debug -output json

# 指定JSON数据路径
go run cmd/importer/main.go -source data/herbs.json -type herbs -json-path data.items

# 指定XML记录元素名称
go run cmd/importer/main.go -source data/herbs.xml -type herbs -xml-record herb
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|-------|
| -source | 数据源文件路径 | 必填 |
| -type | 导入类型 (herbs, formulas) | 必填 |
| -format | 数据格式 (auto, csv, json, xml) | auto |
| -dry-run | 仅测试，不写入数据库 | false |
| -log-level | 日志级别 (debug, info, warn, error) | info |
| -output | 输出格式 (console, json) | console |
| -json-path | JSON数据路径，如 data.items | "" |
| -xml-record | XML记录元素名称 | "" |

## 中药导入器

中药导入器用于导入中药数据，创建中药节点，并建立相关关系。

### 中药数据字段

以下是中药数据的字段映射：

| 字段 | 说明 | 示例值 |
|------|------|-------|
| 名称 | 中药名称 | 黄芪 |
| 拼音 | 中药拼音 | huáng qí |
| 英文名 | 英文名称 | Astragalus |
| 拉丁名 | 拉丁学名 | Astragalus membranaceus |
| 别名 | 别名，用分号分隔 | 黄耆;棉芪;绵芪 |
| 性味 | 药性和味道，用分号分隔 | 性温;味甘 |
| 归经 | 归经，用分号分隔 | 脾经;肺经 |
| 功效 | 功效，用分号分隔 | 补气;固表;利水;托毒;排脓 |
| 主治 | 主治，用分号分隔 | 气虚乏力;食少便溏;中气下陷;脱肛;子宫脱垂 |
| 用法用量 | 用法用量 | 9-30g |
| 禁忌 | 禁忌，用分号分隔 | 表实邪盛;热盛;阴虚火旺 |
| 描述 | 描述信息 | 黄芪为豆科植物蒙古黄芪或膜荚黄芪的干燥根... |
| 来源 | 数据来源 | 中国药典2020版 |
| 标签 | 标签，用分号分隔 | 补气药;利水渗湿药 |
| 相关中药 | 相关中药，用分号分隔 | 党参;白术;人参 |

### 中药导入器使用示例

```go
// 创建中药导入器
herbImporter := importer.NewHerbImporter(
    nodeRepo,
    relRepo,
    logger,
    importer.DefaultHerbFields(), // 使用默认字段映射
)

// 设置导入选项
options := importer.DefaultImportOptions()
options.BatchSize = 100          // 批量处理大小
options.CreateRelations = true   // 创建关系
options.UpdateExisting = false   // 不更新已存在的节点

// 导入数据
stats, err := herbImporter.Import(ctx, "data/herbs.csv", options)
if err != nil {
    log.Fatalf("导入失败: %v", err)
}

// 输出导入统计
fmt.Printf("导入完成: 总数 %d, 成功 %d, 失败 %d\n", 
    stats.TotalCount, 
    stats.SuccessCount, 
    stats.FailedCount)
```

### 中药关系类型

中药导入器会自动创建以下关系：

| 关系类型 | 源节点 | 目标节点 | 说明 |
|---------|-------|---------|------|
| SIMILAR_TO | 中药 | 中药 | 相似中药关系 |
| PART_OF | 中药 | 分类 | 中药属于某个分类 |
| TREATS | 中药 | 症状 | 中药治疗的症状 |
| HAS_PROPERTY | 中药 | 属性 | 中药的性味、归经等属性 |

## 方剂导入器

方剂导入器用于导入方剂数据，创建方剂节点，自动解析方剂组成中的中药，并创建方剂与中药的关系。

### 方剂数据字段

以下是方剂数据的字段映射：

| 字段 | 说明 | 示例值 |
|------|------|-------|
| 名称 | 方剂名称 | 四君子汤 |
| 英文名 | 英文名称 | Four Gentlemen Decoction |
| 别名 | 别名，用分号分隔 | 君子汤;人参汤 |
| 分类 | 方剂分类 | 补气剂 |
| 组成 | 组成成分，中药名及用量 | 人参15g;白术15g;茯苓15g;甘草5g |
| 制法 | 制作方法 | 水煎服，日1剂 |
| 用量 | 用法用量 | 每日1剂，分2次服用 |
| 功效 | 功效，用分号分隔 | 补脾益气;健脾和胃 |
| 主治 | 主治，用分号分隔 | 脾胃气虚;倦怠乏力;食欲不振;体倦乏力 |
| 禁忌 | 禁忌，用分号分隔 | 表实邪盛;湿热偏盛 |
| 来源 | 数据来源 | 《太平惠民和剂局方》 |
| 描述 | 描述信息 | 四君子汤为古代补益脾胃的基础方... |
| 标签 | 标签，用分号分隔 | 补气;健脾 |
| 相关方剂 | 相关方剂，用分号分隔 | 六君子汤;参苓白术散 |

### 方剂导入器使用示例

```go
// 创建方剂导入器
formulaImporter := importer.NewFormulaImporter(
    nodeRepo,
    relRepo,
    logger,
    importer.DefaultFormulaFields(), // 使用默认字段映射
)

// 设置导入选项
options := importer.DefaultImportOptions()
options.BatchSize = 50           // 批量处理大小
options.CreateRelations = true   // 创建关系

// 导入数据
stats, err := formulaImporter.Import(ctx, "data/formulas.json", options)
if err != nil {
    log.Fatalf("导入失败: %v", err)
}

// 输出导入统计
fmt.Printf("导入完成: 总数 %d, 成功 %d, 失败 %d\n", 
    stats.TotalCount, 
    stats.SuccessCount, 
    stats.FailedCount)
```

### 方剂解析器特性

方剂导入器集成了专门的解析逻辑，能自动解析方剂组成中的中药和用量信息：

```go
// 方剂组成字符串示例
"人参10g;茯苓15g;白术15g;甘草6g"

// 解析结果
[
    {"HerbName": "人参", "Dosage": "10g"},
    {"HerbName": "茯苓", "Dosage": "15g"},
    {"HerbName": "白术", "Dosage": "15g"},
    {"HerbName": "甘草", "Dosage": "6g"}
]
```

同时支持多种分隔符格式，如分号(;)、逗号(,)、顿号(、)等。

### 方剂关系类型

方剂导入器会自动创建以下关系：

| 关系类型 | 源节点 | 目标节点 | 说明 |
|---------|-------|---------|------|
| CONTAINS | 方剂 | 中药 | 方剂包含的中药 |
| RELATED_TO | 方剂 | 方剂 | 相关方剂关系 |
| SIMILAR_FUNCTION | 方剂 | 方剂 | 功效相似的方剂 |
| TREATS | 方剂 | 症状 | 方剂治疗的症状 |

## 导入选项

以下是导入器支持的配置选项：

```go
// ImportOptions 导入选项
type ImportOptions struct {
    BatchSize       int       // 批量处理大小
    CreateRelations bool      // 是否创建关系
    UpdateExisting  bool      // 是否更新已存在的节点
    SkipDuplicates  bool      // 是否跳过重复数据
    Validator       Validator // 自定义验证器
}

// 使用默认选项
options := importer.DefaultImportOptions()

// 自定义选项
options.BatchSize = 200
options.CreateRelations = true
options.UpdateExisting = false
options.SkipDuplicates = true
```

## 导入统计信息

导入过程完成后，可以获取详细的统计信息：

```go
// ImportStats 导入统计信息
type ImportStats struct {
    StartTime      time.Time     // 开始时间
    EndTime        time.Time     // 结束时间
    Duration       time.Duration // 持续时间
    TotalCount     int           // 总记录数
    SuccessCount   int           // 成功数
    FailedCount    int           // 失败数
    SkippedCount   int           // 跳过数
    NodesCreated   int           // 创建的节点数
    NodesUpdated   int           // 更新的节点数
    RelsCreated    int           // 创建的关系数
    ProcessedFiles []string      // 处理的文件
    Warnings       []string      // 警告信息
    Errors         []string      // 错误信息
}
```

## 自定义导入器

如果需要导入其他类型的数据，可以通过实现`Importer`接口来创建自定义导入器：

```go
// Importer 导入器接口
type Importer interface {
    // 返回导入器名称
    Name() string
    
    // 返回支持的文件格式
    SupportedFormats() []string
    
    // 验证数据源
    Validate(source string) (bool, []string, error)
    
    // 导入数据
    Import(ctx context.Context, source string, options ImportOptions) (ImportStats, error)
    
    // 从已解析的数据导入
    ImportFromData(ctx context.Context, data []map[string]interface{}, source string, options ImportOptions) (ImportStats, error)
}
```

自定义导入器示例：

```go
type CustomImporter struct {
    *importer.BaseImporter
    nodeRepo repositories.NodeRepository
    relRepo  repositories.RelationshipRepository
    logger   *zap.Logger
    fields   map[string]string
}

func NewCustomImporter(
    nodeRepo repositories.NodeRepository,
    relRepo repositories.RelationshipRepository,
    logger *zap.Logger,
) *CustomImporter {
    return &CustomImporter{
        BaseImporter: importer.NewBaseImporter(nodeRepo, relRepo, logger),
        nodeRepo:     nodeRepo,
        relRepo:      relRepo,
        logger:       logger,
        fields:       customFieldMapping(),
    }
}

func (c *CustomImporter) Name() string {
    return "自定义导入器"
}

func (c *CustomImporter) SupportedFormats() []string {
    return []string{".csv", ".json"}
}

func (c *CustomImporter) Import(ctx context.Context, source string, options importer.ImportOptions) (importer.ImportStats, error) {
    // 实现导入逻辑
    // ...
    return c.Stats, nil
}
```

## 常见问题与解决方案

### 1. 导入大量数据时性能问题

当导入大量数据时，可能会遇到性能问题。以下是一些优化建议：

- 增加批处理大小: `options.BatchSize = 500`
- 避免创建大量临时对象
- 使用内存缓存减少数据库查询

### 2. 解决数据字段不匹配问题

如果源数据的字段名与默认字段映射不匹配，可以自定义字段映射：

```go
// 自定义字段映射
customFields := map[string]string{
    "Name":           "药名",      // 使用"药名"替代"名称"
    "LatinName":      "拉丁学名",   // 使用"拉丁学名"替代"拉丁名"
    "EnglishName":    "英文名称",   // 使用"英文名称"替代"英文名"
    "Functions":      "主要功能",   // 使用"主要功能"替代"功效"
    // ...
}

// 创建导入器时使用自定义字段映射
herbImporter := importer.NewHerbImporter(nodeRepo, relRepo, logger, customFields)
```

### 3. 处理重复数据

当导入的数据中存在重复项时，可以选择跳过或更新：

```go
// 跳过重复数据
options.SkipDuplicates = true

// 更新已存在的节点
options.UpdateExisting = true
```

## 最佳实践

1. **数据清洗**: 在导入前确保数据已经过清洗，特别是处理空值、异常值和格式不一致的问题

2. **增量导入**: 对于大型数据集，考虑使用增量导入策略，只处理新增或更改的数据

3. **适当的批处理大小**: 根据数据复杂度和硬件资源调整批处理大小

4. **错误处理**: 导入完成后，检查导入统计中的警告和错误信息，解决数据问题

5. **测试运行**: 在正式导入前，使用`-dry-run`选项进行测试运行

6. **事务管理**: 对于关键数据，使用事务确保数据一致性

7. **日志监控**: 设置适当的日志级别，监控导入进度和问题