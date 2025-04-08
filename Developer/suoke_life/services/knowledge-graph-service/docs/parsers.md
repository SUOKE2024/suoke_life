# 知识图谱导入工具解析器使用指南

知识图谱导入工具支持多种数据格式的解析，包括CSV、JSON和XML。本文档提供了各种解析器的详细使用说明和示例。

## 解析器概览

导入工具支持以下数据格式：

| 格式 | 解析器 | 说明 |
|------|-------|------|
| CSV | CSVParser | 解析逗号分隔值文件 |
| JSON | JSONParser | 解析JSON数组或对象文件 |
| XML | XMLParser | 解析XML结构化数据文件 |

导入工具会根据文件扩展名自动选择适当的解析器：
- `.csv` - 使用CSVParser
- `.json` - 使用JSONParser
- `.xml` 或 `.rdf` - 使用XMLParser

## CSV解析器

CSV解析器用于处理标准的逗号分隔值文件，支持自定义分隔符、引号和转义字符。

### CSV解析选项

| 选项 | 类型 | 描述 | 默认值 |
|------|------|------|-------|
| HasHeader | bool | 是否包含标题行 | true |
| Delimiter | rune | 字段分隔符 | ',' |
| Comment | rune | 注释字符 | '#' |
| TrimSpace | bool | 是否移除字段前后空白 | true |
| SkipEmptyRows | bool | 是否跳过空行 | true |
| Encoding | string | 编码格式 | "utf8" |

### CSV示例

```csv
名称,拼音,性味,归经,功效
当归,dang gui,温;甘、辛,肝;心;脾,补血;活血;调经
人参,ren shen,微温;甘、微苦,脾;肺,大补元气;复脉固脱;补脾益肺
黄芪,huang qi,微温;甘,脾;肺,补气升阳;固表止汗;利水消肿
```

### CSV解析器使用示例

```go
// 定义解析选项
options := &parsers.CSVParseOptions{
    HasHeader: true,
    Delimiter: ',',
    TrimSpace: true,
}

// 创建解析器
parser := parsers.NewCSVParser("data/herbs.csv", options, logger)

// 解析CSV文件
if err := parser.Parse(); err != nil {
    log.Fatalf("解析CSV失败: %v", err)
}

// 获取解析结果
rows, err := parser.GetRowsAsMap()
if err != nil {
    log.Fatalf("获取数据失败: %v", err)
}

// 处理解析结果
for _, row := range rows {
    // row是map[string]interface{}类型
    fmt.Printf("名称: %s, 拼音: %s\n", row["名称"], row["拼音"])
}
```

## JSON解析器

JSON解析器支持两种主要的JSON数据结构：
1. JSON数组 - 每个数组元素对应一条记录
2. JSON对象 - 包含数组字段的嵌套对象，可通过路径指定

### JSON解析选项

| 选项 | 类型 | 描述 | 默认值 |
|------|------|------|-------|
| RootArrayPath | string | 包含数据的JSON路径 (如 "data.items") | "" (根对象) |
| HeaderFields | []string | 强制使用这些字段作为标题 | [] |

### JSON示例

**数组格式**：
```json
[
  {
    "名称": "当归",
    "拼音": "dang gui",
    "性味": ["温", "甘", "辛"],
    "归经": ["肝经", "心经", "脾经"],
    "功效": ["补血", "活血", "调经"]
  },
  {
    "名称": "人参",
    "拼音": "ren shen",
    "性味": ["微温", "甘", "微苦"],
    "归经": ["脾经", "肺经"],
    "功效": ["大补元气", "复脉固脱", "补脾益肺"]
  }
]
```

**嵌套对象格式**：
```json
{
  "中药": {
    "items": [
      {
        "名称": "当归",
        "拼音": "dang gui",
        "性味": ["温", "甘", "辛"],
        "归经": ["肝经", "心经", "脾经"],
        "功效": ["补血", "活血", "调经"]
      },
      {
        "名称": "人参",
        "拼音": "ren shen",
        "性味": ["微温", "甘", "微苦"],
        "归经": ["脾经", "肺经"],
        "功效": ["大补元气", "复脉固脱", "补脾益肺"]
      }
    ]
  }
}
```

### JSON解析器使用示例

```go
// 定义解析选项
options := &parsers.JSONParseOptions{
    RootArrayPath: "中药.items", // 对于嵌套对象格式
    // 数组格式的JSON不需要指定RootArrayPath
}

// 创建解析器
parser := parsers.NewJSONParser("data/herbs.json", options, logger)

// 解析JSON文件
if err := parser.Parse(); err != nil {
    log.Fatalf("解析JSON失败: %v", err)
}

// 获取解析结果
rows, err := parser.GetRowsAsMap()
if err != nil {
    log.Fatalf("获取数据失败: %v", err)
}

// 处理解析结果
for _, row := range rows {
    // 处理数组字段
    effects, _ := row["功效"].([]interface{})
    effectsStr := make([]string, len(effects))
    for i, effect := range effects {
        effectsStr[i] = effect.(string)
    }
    
    fmt.Printf("名称: %s, 功效: %s\n", row["名称"], strings.Join(effectsStr, ", "))
}
```

## XML解析器

XML解析器支持复杂的XML结构，能够提取XML元素的属性、内容和嵌套元素。

### XML解析选项

| 选项 | 类型 | 描述 | 默认值 |
|------|------|------|-------|
| RootElement | string | 根元素名称 | "" (自动检测) |
| RecordElement | string | 记录元素名称 | "" (自动检测) |
| AttributesAsFields | bool | 是否将XML属性作为字段 | true |
| IncludeXMLTextFields | bool | 是否包含XML元素的文本内容 | false |
| HeaderFields | []string | 强制使用这些字段作为标题 | [] |

### XML示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<中药列表>
  <中药 id="h001">
    <名称>当归</名称>
    <拼音>dang gui</拼音>
    <性味>温;甘、辛</性味>
    <归经>
      <经络>肝经</经络>
      <经络>心经</经络>
      <经络>脾经</经络>
    </归经>
    <功效>
      <作用>补血</作用>
      <作用>活血</作用>
      <作用>调经</作用>
    </功效>
  </中药>
  <中药 id="h002">
    <名称>人参</名称>
    <拼音>ren shen</拼音>
    <性味>微温;甘、微苦</性味>
    <归经>
      <经络>脾经</经络>
      <经络>肺经</经络>
    </归经>
    <功效>
      <作用>大补元气</作用>
      <作用>复脉固脱</作用>
      <作用>补脾益肺</作用>
    </功效>
  </中药>
</中药列表>
```

### XML解析器使用示例

```go
// 定义解析选项
options := &parsers.XMLParseOptions{
    RootElement: "中药列表",
    RecordElement: "中药",
    AttributesAsFields: true,
    IncludeXMLTextFields: true,
}

// 创建解析器
parser := parsers.NewXMLParser("data/herbs.xml", options, logger)

// 解析XML文件
if err := parser.Parse(); err != nil {
    log.Fatalf("解析XML失败: %v", err)
}

// 获取解析结果
rows, err := parser.GetRowsAsMap()
if err != nil {
    log.Fatalf("获取数据失败: %v", err)
}

// 处理解析结果
for _, row := range rows {
    // 获取ID属性和名称
    id := row["id"].(string)
    name := row["名称"].(string)
    
    // 处理嵌套元素列表
    effects := row["功效.作用"].([]interface{})
    effectsStr := make([]string, len(effects))
    for i, effect := range effects {
        effectsStr[i] = effect.(string)
    }
    
    fmt.Printf("ID: %s, 名称: %s, 功效: %s\n", id, name, strings.Join(effectsStr, ", "))
}
```

## 解析器工厂

解析器工厂（ParserFactory）是一个便捷工具，可以根据文件扩展名自动选择适当的解析器。它支持所有上述解析器格式，并简化了解析过程。

### 使用解析器工厂

```go
import (
	"fmt"
	"log"
	
	"suoke.life/services/knowledge-graph-service/internal/importer/parsers"
	"go.uber.org/zap"
)

func main() {
	logger, _ := zap.NewDevelopment()
	
	// 创建解析器工厂
	factory := parsers.NewParserFactory(logger)
	
	// 自动选择适当的解析器
	parser, err := factory.CreateParser("data/herbs.csv", nil)
	if err != nil {
		log.Fatalf("创建解析器失败: %v", err)
	}
	
	// 解析文件
	if err := parser.Parse(); err != nil {
		log.Fatalf("解析文件失败: %v", err)
	}
	
	// 获取解析结果
	rows, err := parser.GetRowsAsMap()
	if err != nil {
		log.Fatalf("获取数据失败: %v", err)
	}
	
	// 处理解析结果
	fmt.Printf("成功解析 %d 条记录\n", len(rows))
	for i, row := range rows {
		if i >= 3 {
			break // 只显示前3条记录
		}
		fmt.Printf("记录 #%d: %v\n", i+1, row)
	}
}
```

### 提供自定义解析选项

您可以针对不同的文件格式提供自定义解析选项：

```go
// 创建CSV解析选项
csvOptions := parsers.CSVParseOptions{
	Delimiter: ';', // 使用分号作为分隔符
	HasHeader: true,
	TrimSpace: true,
}

// 创建JSON解析选项
jsonOptions := parsers.JSONParseOptions{
	RootArrayPath: "data.herbs", // 指定数据路径
}

// 创建XML解析选项
xmlOptions := parsers.XMLParseOptions{
	RecordElement: "herb", // 指定记录元素名称
	AttributesAsFields: true,
}

// 根据文件类型创建适当的解析器并传入相应选项
factory := parsers.NewParserFactory(logger)

// 使用不同选项解析不同文件
csvParser, _ := factory.CreateParser("data/herbs.csv", &csvOptions)
jsonParser, _ := factory.CreateParser("data/formulas.json", &jsonOptions)
xmlParser, _ := factory.CreateParser("data/symptoms.xml", &xmlOptions)
```

### 支持的文件类型

ParserFactory根据文件扩展名自动选择适当的解析器：

| 文件扩展名 | 自动选择的解析器 | 常量 |
|------------|-----------------|------|
| `.csv`, `.tsv`, `.txt` | CSVParser | `parsers.FileTypeCSV` |
| `.json` | JSONParser | `parsers.FileTypeJSON` |
| `.xml` | XMLParser | `parsers.FileTypeXML` |
| 其他 | 返回错误 | `parsers.FileTypeUnknown` |

### 在导入器中使用解析器工厂

知识图谱导入工具的导入器（如`HerbImporter`和`FormulaImporter`）已经集成了解析器工厂，可以自动处理CSV、JSON和XML等多种格式的文件。您只需提供数据文件路径，导入器会自动选择合适的解析器。

例如，这些导入器都支持以下文件格式：
- 中药数据: `.csv`, `.json`, `.xml`, `.txt`
- 方剂数据: `.csv`, `.json`, `.xml`, `.txt`

这意味着您可以使用相同的导入命令处理不同格式的文件，而无需指定格式类型。