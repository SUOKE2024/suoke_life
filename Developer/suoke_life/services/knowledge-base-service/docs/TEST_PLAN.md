# 知识库服务测试计划

本文档详细描述了知识库服务的测试计划，包括单元测试、集成测试、性能测试和负载测试的具体实施方案。

## 1. 测试目标

- 确保知识库服务的所有功能正常工作
- 验证服务的性能和可扩展性
- 确保数据的一致性和完整性
- 验证系统在高负载下的稳定性
- 达到至少85%的代码覆盖率

## 2. 测试类型

### 2.1 单元测试

单元测试用于验证独立的代码单元（如函数、方法或类）的正确性。

#### 2.1.1 领域层测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| 实体验证 | 测试实体创建、属性验证和业务规则 | `internal/domain/entity/` |
| 存储库接口 | 测试存储库接口的契约 | `internal/domain/repository/` |
| 领域服务 | 测试领域逻辑和业务规则 | `internal/domain/service/` |
| 值对象 | 测试值对象的不变性和等值比较 | `internal/domain/valueobject/` |

#### 2.1.2 应用层测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| 用例服务 | 测试应用用例和协调逻辑 | `internal/application/usecase/` |
| 命令处理 | 测试命令处理器和验证 | `internal/application/command/` |
| 查询处理 | 测试查询处理器和结果映射 | `internal/application/query/` |
| DTO映射 | 测试数据传输对象的映射逻辑 | `internal/application/dto/` |

#### 2.1.3 基础设施层测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| 持久化实现 | 使用内存数据库测试存储库实现 | `internal/infrastructure/repository/` |
| API处理器 | 测试HTTP处理器和请求解析 | `internal/infrastructure/api/` |
| 外部服务适配器 | 使用模拟服务测试外部服务集成 | `internal/infrastructure/service/` |
| 工具函数 | 测试辅助函数和工具 | `pkg/` |

#### 2.1.4 单元测试示例

```go
func TestDocumentEntity_Validate(t *testing.T) {
	tests := []struct {
		name    string
		doc     entity.Document
		wantErr bool
	}{
		{
			name: "有效文档",
			doc: entity.Document{
				ID:       "doc123",
				Title:    "测试文档",
				Content:  "这是测试内容",
				Category: "测试分类",
			},
			wantErr: false,
		},
		{
			name: "标题为空",
			doc: entity.Document{
				ID:       "doc123",
				Title:    "",
				Content:  "这是测试内容",
				Category: "测试分类",
			},
			wantErr: true,
		},
		// 更多测试用例...
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.doc.Validate()
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
```

### 2.2 集成测试

集成测试用于验证多个组件集成在一起时的正确性。

#### 2.2.1 数据库集成测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| 持久化存储 | 使用Docker容器运行PostgreSQL测试存储库 | `internal/infrastructure/repository/postgres/` |
| 事务管理 | 测试事务提交和回滚 | `internal/infrastructure/repository/postgres/` |
| 查询性能 | 测试复杂查询的执行和性能 | `internal/infrastructure/repository/postgres/` |

#### 2.2.2 向量存储集成测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| 向量索引 | 使用Docker容器运行Milvus测试向量存储 | `internal/infrastructure/vectorstore/` |
| 相似度搜索 | 测试向量相似度搜索功能 | `internal/infrastructure/vectorstore/` |
| 批量操作 | 测试批量索引和查询 | `internal/infrastructure/vectorstore/` |

#### 2.2.3 API集成测试

| 测试目标 | 测试策略 | 覆盖范围 |
|---------|---------|---------|
| HTTP处理器 | 测试API端点和请求处理 | `internal/api/` |
| 中间件 | 测试认证和请求处理中间件 | `internal/api/middleware/` |
| 响应格式 | 测试API响应格式和错误处理 | `internal/api/response/` |

#### 2.2.4 集成测试示例

```go
// 使用标签跳过普通测试
// +build integration

package postgres_test

import (
	"context"
	"database/sql"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/infrastructure/repository/postgres"
)

func setupTestDB(t *testing.T) (*sql.DB, func()) {
	// 使用testcontainers启动PostgreSQL容器
	ctx := context.Background()
	postgresContainer := testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "postgres:14-alpine",
			ExposedPorts: []string{"5432/tcp"},
			Env: map[string]string{
				"POSTGRES_USER":     "testuser",
				"POSTGRES_PASSWORD": "testpass",
				"POSTGRES_DB":       "testdb",
			},
			WaitingFor: wait.ForLog("database system is ready to accept connections"),
		},
		Started: true,
	}

	container, err := testcontainers.GenericContainer(ctx, postgresContainer)
	require.NoError(t, err)

	port, err := container.MappedPort(ctx, "5432")
	require.NoError(t, err)

	host, err := container.Host(ctx)
	require.NoError(t, err)

	connectionString := fmt.Sprintf("postgresql://testuser:testpass@%s:%s/testdb?sslmode=disable", host, port.Port())
	
	// 连接数据库
	db, err := sql.Open("postgres", connectionString)
	require.NoError(t, err)
	
	// 运行迁移脚本
	// ...

	// 返回清理函数
	cleanup := func() {
		db.Close()
		container.Terminate(ctx)
	}

	return db, cleanup
}

func TestDocumentRepository_Integration(t *testing.T) {
	db, cleanup := setupTestDB(t)
	defer cleanup()

	// 创建存储库实例
	repo := postgres.NewDocumentRepository(db)

	// 测试创建文档
	doc := entity.Document{
		ID:        "test-doc-1",
		Title:     "测试文档",
		Content:   "这是一个测试文档的内容",
		Category:  "测试分类",
		Tags:      []string{"测试", "集成测试"},
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	err := repo.Create(context.Background(), &doc)
	assert.NoError(t, err)

	// 测试获取文档
	retrieved, err := repo.GetByID(context.Background(), "test-doc-1")
	assert.NoError(t, err)
	assert.Equal(t, doc.Title, retrieved.Title)
	assert.Equal(t, doc.Content, retrieved.Content)
	assert.Equal(t, doc.Category, retrieved.Category)
	assert.Equal(t, len(doc.Tags), len(retrieved.Tags))

	// 更多测试...
}
```

### 2.3 性能测试

性能测试用于评估系统在不同负载条件下的响应时间和资源利用率。

#### 2.3.1 基准测试

| 测试目标 | 测试策略 | 指标 |
|---------|---------|------|
| API响应时间 | 使用Go的基准测试测量API响应时间 | 平均响应时间、p95、p99 |
| 数据库操作 | 测量数据库查询和更新的性能 | 查询时间、写入速度 |
| 向量检索 | 测量向量相似度搜索的性能 | 查询时间、召回率、精确度 |

#### 2.3.2 性能测试示例

```go
func BenchmarkDocumentRepository_Search(b *testing.B) {
	// 设置测试环境
	db, _ := setupTestDB(b)
	defer db.Close()
	
	repo := postgres.NewDocumentRepository(db)
	
	// 准备测试数据
	prepareTestDocuments(b, repo, 1000)
	
	ctx := context.Background()
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		results, err := repo.Search(ctx, "中医", 1, 20, "", nil)
		if err != nil {
			b.Fatal(err)
		}
		if len(results) == 0 {
			b.Fatal("No results found")
		}
	}
}

func BenchmarkVectorStore_SemanticSearch(b *testing.B) {
	// 设置测试环境
	client, _ := setupTestMilvus(b)
	
	store := vectorstore.NewMilvusVectorStore(client, "test_collection")
	
	// 准备测试数据
	prepareTestVectors(b, store, 1000)
	
	ctx := context.Background()
	
	// 准备测试查询向量
	queryVector := generateQueryVector()
	
	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		results, err := store.Search(ctx, queryVector, 10, 0.7)
		if err != nil {
			b.Fatal(err)
		}
		if len(results) == 0 {
			b.Fatal("No results found")
		}
	}
}
```

### 2.4 负载测试

负载测试用于评估系统在高并发和持续负载下的稳定性和性能。

#### 2.4.1 负载测试计划

| 测试场景 | 测试策略 | 指标 |
|---------|---------|------|
| 并发读取 | 模拟多用户同时读取内容 | 吞吐量、响应时间、错误率 |
| 并发写入 | 模拟多用户同时创建和更新内容 | 吞吐量、响应时间、错误率 |
| 混合负载 | 模拟真实用户行为的混合负载 | 服务器CPU/内存利用率、响应时间 |
| 长时间运行 | 持续运行测试以检测内存泄漏 | 内存使用增长、响应时间稳定性 |

#### 2.4.2 负载测试工具

- 使用K6或Apache JMeter执行HTTP负载测试
- 使用Prometheus和Grafana监控系统资源
- 使用pprof分析Go程序性能瓶颈

#### 2.4.3 负载测试脚本示例 (K6)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },   // 逐步提升到50个虚拟用户
    { duration: '3m', target: 50 },   // 保持50个虚拟用户3分钟
    { duration: '1m', target: 100 },  // 提升到100个虚拟用户
    { duration: '5m', target: 100 },  // 保持100个虚拟用户5分钟
    { duration: '1m', target: 0 },    // 逐步减少到0个虚拟用户
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95%的请求应在500ms内完成
    http_req_failed: ['rate<0.01'],     // 错误率应低于1%
  },
};

const BASE_URL = 'https://staging.api.suoke.life/kb/api/v1';
const TOKEN = '${__ENV.API_TOKEN}';

export default function() {
  let searchQuery = '中医养生';
  
  // 模拟搜索请求
  let searchResponse = http.get(`${BASE_URL}/documents/search?q=${searchQuery}&limit=10`, {
    headers: { 'Authorization': `Bearer ${TOKEN}` },
  });
  
  check(searchResponse, {
    'search status is 200': (r) => r.status === 200,
    'search returns results': (r) => JSON.parse(r.body).data.items.length > 0,
  });
  
  // 随机睡眠1-5秒模拟用户行为
  sleep(Math.random() * 4 + 1);
  
  // 如果搜索成功，获取第一个文档的详情
  if (searchResponse.status === 200) {
    let items = JSON.parse(searchResponse.body).data.items;
    if (items.length > 0) {
      let docId = items[0].id;
      
      let docResponse = http.get(`${BASE_URL}/documents/${docId}`, {
        headers: { 'Authorization': `Bearer ${TOKEN}` },
      });
      
      check(docResponse, {
        'document status is 200': (r) => r.status === 200,
        'document has content': (r) => JSON.parse(r.body).data.content.length > 0,
      });
    }
  }
  
  // 再次随机睡眠
  sleep(Math.random() * 4 + 1);
}
```

## 3. 测试环境

### 3.1 本地测试环境

- Go测试框架
- Docker容器化的依赖服务(PostgreSQL, Milvus)
- 模拟外部服务的替代实现

### 3.2 CI/CD测试环境

- GitHub Actions运行的自动化测试
- 测试覆盖率报告
- 性能基准测试结果收集

### 3.3 预发布环境测试

- 部署到与生产环境相同配置的预发布环境
- 执行端到端测试和负载测试
- 使用生产数据的匿名副本进行测试

## 4. 测试数据管理

### 4.1 测试数据准备

- 使用数据生成器创建符合领域规则的测试数据
- 为各种测试场景准备专用测试数据集
- 准备边缘情况和异常情况的测试数据

### 4.2 测试数据生成工具

```go
package testdata

import (
	"math/rand"
	"time"
	
	"knowledge-base-service/internal/domain/entity"
)

var (
	categories = []string{"中医理论", "养生保健", "食疗方案", "运动健康", "心理健康"}
	tagSets = map[string][]string{
		"中医理论": {"阴阳", "五行", "气血", "脏腑", "经络", "辨证", "体质"},
		"养生保健": {"四季养生", "起居", "按摩", "穴位", "中药", "情志", "保健"},
		"食疗方案": {"四季饮食", "食材", "食疗", "药膳", "营养", "功效", "调理"},
		// ...其他分类的标签
	}
)

// GenerateTestDocument 生成测试文档
func GenerateTestDocument(id string) entity.Document {
	rand.Seed(time.Now().UnixNano())
	
	category := categories[rand.Intn(len(categories))]
	tags := getRandomTags(category, 2+rand.Intn(3))
	
	return entity.Document{
		ID:        id,
		Title:     generateTitle(category),
		Content:   generateContent(category),
		Summary:   generateSummary(),
		Category:  category,
		Tags:      tags,
		CreatedAt: time.Now().Add(-time.Duration(rand.Intn(30)) * 24 * time.Hour),
		UpdatedAt: time.Now(),
	}
}

// GenerateTestDocuments 批量生成测试文档
func GenerateTestDocuments(count int) []entity.Document {
	docs := make([]entity.Document, count)
	for i := 0; i < count; i++ {
		docs[i] = GenerateTestDocument(fmt.Sprintf("test-doc-%d", i+1))
	}
	return docs
}

// 其他辅助函数...
```

## 5. 测试自动化

### 5.1 CI/CD集成

- 在每次提交时运行单元测试
- 在PR合并前运行集成测试
- 在发布前运行性能测试
- 生成测试覆盖率报告和性能指标

### 5.2 自动化测试配置

```yaml
# .github/workflows/ci-cd.yml 部分内容

  lint-test:
    name: 代码检查与测试
    runs-on: ubuntu-latest
    steps:
      # ...前面的步骤省略
      
      - name: 单元测试
        run: go test -v -race -coverprofile=coverage.out ./...

      - name: 上传测试覆盖率报告
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: coverage-report
          path: coverage.out
  
  vector-db-integration-test:
    name: 向量数据库集成测试
    runs-on: ubuntu-latest
    needs: lint-test
    steps:
      - uses: actions/checkout@v3
      
      - name: 设置Go环境
        uses: actions/setup-go@v4
        with:
          go-version: ${{ env.GO_VERSION }}
          cache: true
      
      - name: 安装依赖
        run: go mod download
      
      - name: 准备测试数据
        run: |
          go run ./cmd/tools/seed_testdata

      - name: 运行集成测试
        env:
          VECTOR_STORE_HOST: localhost
          VECTOR_STORE_PORT: 19530
          VECTOR_STORE_COLLECTION: test_collection
        run: go test -v -tags=integration ./internal/infrastructure/vectorstore/...
```

## 6. 测试报告

### 6.1 测试覆盖率报告

- 使用Go的内置覆盖率工具生成报告
- 在CI/CD流程中添加覆盖率门槛检查
- 展示覆盖率趋势和改进情况

### 6.2 性能测试报告

- 记录关键操作的性能基准
- 跟踪性能随时间的变化
- 识别性能退化并及时报警

### 6.3 Bug跟踪和修复

- 将测试失败与问题跟踪系统集成
- 为每个测试失败创建详细报告
- 跟踪修复进度和验证

## 7. 测试资源

### 7.1 工具和框架

- **测试框架**: Go标准测试库, testify
- **模拟工具**: gomock, httptest
- **性能测试**: Go基准测试, K6
- **容器化测试**: testcontainers-go
- **覆盖率工具**: Go cover工具

### 7.2 学习资源

- [Go测试实践指南](https://github.com/golang/go/wiki/TestComments)
- [Go高级测试模式](https://github.com/golang/go/wiki/TableDrivenTests)
- [使用Testify简化测试](https://github.com/stretchr/testify)
- [负载测试最佳实践](https://k6.io/docs/testing-guides/api-load-testing)

## 8. 测试责任

- **开发人员**: 编写单元测试和集成测试
- **QA工程师**: 设计和执行性能测试和负载测试
- **DevOps工程师**: 维护测试基础设施和监控
- **团队负责人**: 确保测试覆盖率达标和质量门槛

## 9. 时间表

| 阶段 | 活动 | 时间 |
|------|------|------|
| 第1阶段 | 补充核心领域实体和存储库单元测试 | 1周 |
| 第2阶段 | 完善API处理器和应用服务测试 | 1周 |
| 第3阶段 | 开发集成测试框架和基本测试 | 1-2周 |
| 第4阶段 | 开发性能测试和基准测试 | 1周 |
| 第5阶段 | 设置自动化测试和CI/CD集成 | 1周 |
| 第6阶段 | 执行全面的测试计划和覆盖率分析 | 持续 |

## 10. 结论

完善的测试策略对于确保知识库服务的质量和稳定性至关重要。通过结合单元测试、集成测试、性能测试和负载测试，我们可以全面验证系统的功能正确性和性能特性，为用户提供可靠和高效的服务。

测试不仅是质量保证的手段，也是文档化系统行为和期望的方式。通过维护良好的测试套件，我们可以支持持续集成和持续部署，加速开发周期，并减少生产环境中的问题。