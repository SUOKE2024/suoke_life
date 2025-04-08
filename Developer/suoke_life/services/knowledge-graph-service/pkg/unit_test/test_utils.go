// Package unit_test 提供单元测试和集成测试的通用工具
package unit_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"github.com/stretchr/testify/require"
	"go.uber.org/zap"
	"go.uber.org/zap/zaptest"

	"knowledge-graph-service/internal/infrastructure/database"
)

// TestLogger 创建测试logger
func TestLogger(t *testing.T) *zap.Logger {
	return zaptest.NewLogger(t)
}

// TestLoggerTimed 创建带有时间输出的测试logger
func TestLoggerTimed(t *testing.T) *zap.Logger {
	return zaptest.NewLogger(t, zaptest.WrapOptions(zap.WithClock(zaptest.NewMockClock())))
}

// SetupTestDB 初始化测试数据库连接
func SetupTestDB(t *testing.T) *database.Neo4jManager {
	// 允许从环境变量获取连接信息
	uri := os.Getenv("TEST_NEO4J_URI")
	if uri == "" {
		uri = "bolt://localhost:7687"
	}

	username := os.Getenv("TEST_NEO4J_USERNAME")
	if username == "" {
		username = "neo4j"
	}

	password := os.Getenv("TEST_NEO4J_PASSWORD")
	if password == "" {
		password = "password"
	}

	dbName := os.Getenv("TEST_NEO4J_DB")
	if dbName == "" {
		dbName = "neo4j"
	}

	config := database.Neo4jConfig{
		URI:      uri,
		Username: username,
		Password: password,
		Database: dbName,
	}

	// 创建数据库连接
	db, err := database.NewNeo4jManager(config)
	require.NoError(t, err, "连接测试数据库失败")
	require.NotNil(t, db, "数据库连接为空")

	// 清理测试数据库
	ctx := context.Background()
	CleanupTestDB(t, db)

	return db
}

// CleanupTestDB 清理测试数据库
func CleanupTestDB(t *testing.T, db *database.Neo4jManager) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	// 删除所有节点和关系
	cypher := `
		MATCH (n)
		DETACH DELETE n
		RETURN count(n) as deleted
	`
	
	result, err := db.ExecuteWrite(ctx, cypher, nil)
	require.NoError(t, err, "清理测试数据库失败")
	
	records := result.([]neo4j.Record)
	require.NotEmpty(t, records, "清理测试数据库结果为空")
	
	deleted, ok := records[0].Get("deleted")
	require.True(t, ok, "清理测试数据库结果中没有deleted字段")
	
	t.Logf("已删除 %d 个节点", deleted)
}

// CreateTestNode 创建测试节点
func CreateTestNode(t *testing.T, db *database.Neo4jManager, name, category string, properties map[string]interface{}) string {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	if properties == nil {
		properties = make(map[string]interface{})
	}
	
	now := time.Now()
	properties["name"] = name
	properties["category"] = category
	properties["id"] = "test_" + name
	properties["createdAt"] = now
	properties["updatedAt"] = now
	
	cypher := `
		CREATE (n:Node)
		SET n = $props
		RETURN n.id as id
	`
	
	params := map[string]interface{}{
		"props": properties,
	}
	
	result, err := db.ExecuteWrite(ctx, cypher, params)
	require.NoError(t, err, "创建测试节点失败")
	
	records := result.([]neo4j.Record)
	require.NotEmpty(t, records, "创建测试节点结果为空")
	
	id, ok := records[0].Get("id")
	require.True(t, ok, "创建测试节点结果中没有id字段")
	
	return id.(string)
}

// CreateTestRelationship 创建测试关系
func CreateTestRelationship(t *testing.T, db *database.Neo4jManager, fromID, toID, relType string, properties map[string]interface{}) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	if properties == nil {
		properties = make(map[string]interface{})
	}
	
	now := time.Now()
	properties["createdAt"] = now
	
	cypher := `
		MATCH (from:Node {id: $fromID}), (to:Node {id: $toID})
		CREATE (from)-[r:` + relType + `]->(to)
		SET r = $props
		RETURN type(r) as type
	`
	
	params := map[string]interface{}{
		"fromID": fromID,
		"toID":   toID,
		"props":  properties,
	}
	
	result, err := db.ExecuteWrite(ctx, cypher, params)
	require.NoError(t, err, "创建测试关系失败")
	
	records := result.([]neo4j.Record)
	require.NotEmpty(t, records, "创建测试关系结果为空")
	
	relTypeResult, ok := records[0].Get("type")
	require.True(t, ok, "创建测试关系结果中没有type字段")
	require.Equal(t, relType, relTypeResult, "关系类型不匹配")
}

// RequireEqual 断言两个值相等
func RequireEqual(t *testing.T, expected, actual interface{}, msgAndArgs ...interface{}) {
	require.Equal(t, expected, actual, msgAndArgs...)
}

// RequireNoError 断言没有错误
func RequireNoError(t *testing.T, err error, msgAndArgs ...interface{}) {
	require.NoError(t, err, msgAndArgs...)
}

// RequireNotNil 断言值不为nil
func RequireNotNil(t *testing.T, obj interface{}, msgAndArgs ...interface{}) {
	require.NotNil(t, obj, msgAndArgs...)
}

// RequireTrue 断言条件为true
func RequireTrue(t *testing.T, condition bool, msgAndArgs ...interface{}) {
	require.True(t, condition, msgAndArgs...)
}

// RequireFalse 断言条件为false
func RequireFalse(t *testing.T, condition bool, msgAndArgs ...interface{}) {
	require.False(t, condition, msgAndArgs...)
}

// RequireContains 断言集合包含元素
func RequireContains(t *testing.T, haystack, needle interface{}, msgAndArgs ...interface{}) {
	require.Contains(t, haystack, needle, msgAndArgs...)
}

// RequireLen 断言集合长度
func RequireLen(t *testing.T, object interface{}, length int, msgAndArgs ...interface{}) {
	require.Len(t, object, length, msgAndArgs...)
}