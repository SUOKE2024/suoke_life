# Swagger/OpenAPI集成计划

本文档描述了知识库服务集成Swagger/OpenAPI文档系统的计划和具体实施步骤。

## 1. 概述

Swagger/OpenAPI是一种用于描述RESTful API的规范，它允许开发人员使用标准化的方式定义API接口，并自动生成交互式文档。

集成Swagger/OpenAPI将带来以下优势：
- 提供交互式API文档，便于开发人员和客户端使用
- 支持在线测试API功能
- 自动化生成客户端代码
- 标准化API设计和实现
- 简化API版本管理

## 2. 集成方案

对于Go语言开发的知识库服务，我们将使用以下工具和库进行Swagger/OpenAPI集成：

### 2.1 核心工具

- **[swaggo/swag](https://github.com/swaggo/swag)**: 用于Go项目的Swagger文档生成器
- **[swaggo/http-swagger](https://github.com/swaggo/http-swagger)**: 用于go-chi框架的Swagger UI处理器
- **[github.com/go-chi/chi/v5](https://github.com/go-chi/chi)**: Web路由框架

### 2.2 文档位置

- API文档将在以下URL可用：
  - `/api/v1/swagger/index.html`: Swagger UI交互式文档
  - `/api/v1/swagger/doc.json`: OpenAPI规范JSON文件
  - `/api/v1/swagger/doc.yaml`: OpenAPI规范YAML文件

## 3. 实施步骤

### 3.1 安装依赖

安装Swagger工具和相关库：

```bash
# 安装swag命令行工具
go install github.com/swaggo/swag/cmd/swag@latest

# 添加项目依赖
go get -u github.com/swaggo/swag/cmd/swag
go get -u github.com/swaggo/http-swagger
```

### 3.2 项目结构调整

创建Swagger文档主文件：

```go
// cmd/server/main.go 或 internal/api/api.go

// @title          知识库服务API
// @version        1.0
// @description    索克生活知识库服务，提供健康养生知识内容的存储、索引和查询功能。
// @termsOfService https://suoke.life/terms/

// @contact.name  索克生活技术团队
// @contact.url   https://suoke.life/contact
// @contact.email dev@suoke.life

// @license.name 版权所有 © 2024 索克生活
// @license.url  https://suoke.life/license

// @host      api.suoke.life
// @BasePath  /kb/api/v1

// @securityDefinitions.apikey BearerAuth
// @in header
// @name Authorization
// @description 请在值前添加Bearer前缀，例如 "Bearer {token}"
```

### 3.3 注解示例

为每个处理函数添加Swagger注解：

```go
// GetDocumentByID 获取文档详情
// @Summary      获取文档详情
// @Description  根据ID获取文档的完整信息
// @Tags         documents
// @Accept       json
// @Produce      json
// @Param        id   path      string  true  "文档ID"
// @Success      200  {object}  response.Response{data=entity.Document}
// @Failure      400  {object}  response.Response
// @Failure      404  {object}  response.Response
// @Failure      500  {object}  response.Response
// @Router       /documents/{id} [get]
// @Security     BearerAuth
func (h *DocumentHandler) GetDocumentByID(w http.ResponseWriter, r *http.Request) {
    // 处理逻辑...
}
```

### 3.4 路由配置

在路由配置中添加Swagger UI处理器：

```go
func setupRoutes(r *chi.Mux) {
    // 添加Swagger处理器
    r.Get("/api/v1/swagger/*", httpSwagger.Handler(
        httpSwagger.URL("/api/v1/swagger/doc.json"),
        httpSwagger.DeepLinking(true),
        httpSwagger.DocExpansion("none"),
        httpSwagger.DomID("swagger-ui"),
    ))
    
    // 其他路由配置...
}
```

### 3.5 生成Swagger文档

创建生成Swagger文档的命令：

```bash
#!/bin/bash
# scripts/generate_swagger.sh

cd "$(dirname "$0")/.."
swag init -g cmd/server/main.go -o ./docs/swagger
```

将此命令添加到Makefile：

```makefile
.PHONY: swagger
swagger:
	@echo "Generating Swagger documentation..."
	@./scripts/generate_swagger.sh
```

### 3.6 CI/CD集成

在CI/CD流程中增加Swagger文档生成步骤：

```yaml
lint-test:
  name: 代码检查与测试
  runs-on: ubuntu-latest
  steps:
    # 其他步骤...
    
    - name: 生成Swagger文档
      run: make swagger
      
    - name: 验证Swagger文档
      run: |
        if [ ! -f "./docs/swagger/swagger.json" ]; then
          echo "Swagger documentation not generated!"
          exit 1
        fi
```

## 4. 模型定义

为了正确生成API文档，需要定义用于Swagger的模型结构：

```go
// internal/api/model/swagger_models.go

package model

// StandardResponse 标准响应结构
type StandardResponse struct {
	Success bool        `json:"success" example:"true"`
	Code    int         `json:"code" example:"200"`
	Message string      `json:"message" example:"操作成功"`
	Data    interface{} `json:"data,omitempty"`
}

// ErrorResponse 错误响应结构
type ErrorResponse struct {
	Success bool           `json:"success" example:"false"`
	Code    int            `json:"code" example:"400"`
	Message string         `json:"message" example:"请求参数错误"`
	Errors  []FieldError   `json:"errors,omitempty"`
}

// FieldError 字段错误
type FieldError struct {
	Field   string `json:"field" example:"title"`
	Message string `json:"message" example:"标题不能为空"`
}

// PaginatedResponse 分页响应结构
type PaginatedResponse struct {
	Total int         `json:"total" example:"100"`
	Page  int         `json:"page" example:"1"`
	Limit int         `json:"limit" example:"20"`
	Items interface{} `json:"items"`
}

// DocumentListItem 文档列表项
type DocumentListItem struct {
	ID        string   `json:"id" example:"doc123"`
	Title     string   `json:"title" example:"中医体质辨识基础"`
	Summary   string   `json:"summary" example:"介绍九种体质的基本特征和辨识方法"`
	Category  string   `json:"category" example:"中医理论"`
	Tags      []string `json:"tags" example:"体质辨识,中医基础"`
	CreatedAt string   `json:"created_at" example:"2024-04-01T08:00:00Z"`
	UpdatedAt string   `json:"updated_at" example:"2024-04-02T10:30:00Z"`
}

// DocumentDetail 文档详情
type DocumentDetail struct {
	ID               string              `json:"id" example:"doc123"`
	Title            string              `json:"title" example:"中医体质辨识基础"`
	Content          string              `json:"content" example:"中医体质学说是中医学对人体生命本质的认识..."`
	Summary          string              `json:"summary" example:"介绍九种体质的基本特征和辨识方法"`
	Category         string              `json:"category" example:"中医理论"`
	Tags             []string            `json:"tags" example:"体质辨识,中医基础"`
	References       []DocumentReference `json:"references,omitempty"`
	RelatedDocuments []string            `json:"related_documents,omitempty" example:"doc456,doc789"`
	Version          int                 `json:"version" example:"2"`
	CreatedAt        string              `json:"created_at" example:"2024-04-01T08:00:00Z"`
	UpdatedAt        string              `json:"updated_at" example:"2024-04-02T10:30:00Z"`
}

// DocumentReference 文档引用
type DocumentReference struct {
	Title  string `json:"title" example:"《中医体质学》"`
	Author string `json:"author,omitempty" example:"王琦"`
	Year   int    `json:"year,omitempty" example:"2005"`
	URL    string `json:"url,omitempty"`
}

// CreateDocumentRequest 创建文档请求
type CreateDocumentRequest struct {
	Title      string              `json:"title" example:"四季养生之春季养生"`
	Content    string              `json:"content" example:"春季养生应当以养肝为主，饮食宜甘少酸..."`
	Summary    string              `json:"summary" example:"介绍春季养生的基本原则和方法"`
	Category   string              `json:"category" example:"养生保健"`
	Tags       []string            `json:"tags" example:"四季养生,春季,养肝"`
	References []DocumentReference `json:"references,omitempty"`
}

// SearchResult 搜索结果
type SearchResult struct {
	ID        string             `json:"id" example:"doc456"`
	Title     string             `json:"title" example:"四季养生之春季养生指南"`
	Summary   string             `json:"summary" example:"全面介绍春季养生的基本原则和实用方法"`
	Category  string             `json:"category" example:"养生保健"`
	Tags      []string           `json:"tags" example:"四季养生,春季,养肝,实用指南"`
	Highlight map[string]string  `json:"highlight,omitempty"`
	Score     float64            `json:"score,omitempty" example:"0.89"`
	Similarity float64           `json:"similarity,omitempty" example:"0.92"`
}

// CategoryInfo 分类信息
type CategoryInfo struct {
	ID            string `json:"id" example:"cat1"`
	Name          string `json:"name" example:"中医理论"`
	Description   string `json:"description" example:"中医基础理论和概念"`
	DocumentCount int    `json:"document_count" example:"120"`
}

// TagInfo 标签信息
type TagInfo struct {
	ID            string `json:"id" example:"tag1"`
	Name          string `json:"name" example:"四季养生"`
	DocumentCount int    `json:"document_count" example:"45"`
}
```

## 5. 文档样式定制

为了更好地展示API文档，可以通过以下配置自定义Swagger UI样式：

```go
// 自定义UI配置
httpSwagger.UIConfig(map[string]string{
    "apisSorter":          "alpha",
    "operationsSorter":    "method",
    "defaultModelsExpandDepth": "-1",
    "displayRequestDuration": "true",
    "docExpansion":        "none",
    "filter":              "true",
    "layout":              "StandaloneLayout",
    "theme":               "material", // 如果使用SwaggerUI v4+
    "syntaxHighlight.theme": "monokai",
}),
```

## 6. 实施计划

- **第1阶段** (1-2天): 安装依赖并设置基础结构
- **第2阶段** (2-3天): 为现有API端点添加Swagger注解
- **第3阶段** (1天): 生成和验证Swagger文档
- **第4阶段** (1-2天): 集成到CI/CD流程并测试
- **第5阶段** (1天): 美化UI并完善文档

## 7. 维护策略

为确保API文档的质量和时效性，需要采取以下维护策略：

1. 代码审查流程中添加API文档检查
2. 每次API变更必须同步更新Swagger注解
3. CI/CD流程验证Swagger文档生成是否成功
4. 定期检查文档的准确性和完整性
5. 收集用户对API文档的反馈并持续改进

## 8. 总结

通过集成Swagger/OpenAPI文档系统，知识库服务将提供更加标准化和用户友好的API文档，便于开发人员理解和使用API。这不仅提高了API的可用性，也为后续的API版本管理和客户端代码生成奠定了基础。