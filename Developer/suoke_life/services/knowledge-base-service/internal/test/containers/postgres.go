package containers

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	testDBName     = "knowledge_base_test"
	testDBUser     = "test_user"
	testDBPassword = "test_password"
)

// PostgresContainer 封装PostgreSQL测试容器
type PostgresContainer struct {
	container *postgres.PostgresContainer
	connStr   string
}

// StartPostgresContainer 启动PostgreSQL测试容器
func StartPostgresContainer(ctx context.Context) (*PostgresContainer, error) {
	log.Println("正在启动PostgreSQL测试容器...")

	container, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:14-alpine"),
		postgres.WithDatabase(testDBName),
		postgres.WithUsername(testDBUser),
		postgres.WithPassword(testDBPassword),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithStartupTimeout(60*time.Second),
		),
	)

	if err != nil {
		return nil, fmt.Errorf("无法启动PostgreSQL测试容器: %w", err)
	}

	// 获取连接信息
	host, err := container.Host(ctx)
	if err != nil {
		return nil, fmt.Errorf("无法获取PostgreSQL主机地址: %w", err)
	}

	port, err := container.MappedPort(ctx, "5432/tcp")
	if err != nil {
		return nil, fmt.Errorf("无法获取PostgreSQL端口映射: %w", err)
	}

	// 构建连接字符串，确保添加sslmode=disable
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port.Port(), testDBUser, testDBPassword, testDBName)

	log.Printf("PostgreSQL测试容器已启动: %s", connStr)

	return &PostgresContainer{
		container: container,
		connStr:   connStr,
	}, nil
}

// ConnectionString 返回数据库连接字符串
func (pc *PostgresContainer) ConnectionString() string {
	return pc.connStr
}

// Stop 停止并移除容器
func (pc *PostgresContainer) Stop(ctx context.Context) error {
	log.Println("正在停止PostgreSQL测试容器...")
	return pc.container.Terminate(ctx)
}
