package containers

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

const (
	milvusImage = "milvusdb/milvus:v2.2.11"
	milvusPort  = "19530"
)

// MilvusContainer 封装Milvus向量数据库测试容器
type MilvusContainer struct {
	container testcontainers.Container
	host      string
	port      string
}

// StartMilvusContainer 启动Milvus测试容器
func StartMilvusContainer(ctx context.Context) (*MilvusContainer, error) {
	log.Println("正在启动Milvus测试容器...")

	// 设置容器配置
	req := testcontainers.ContainerRequest{
		Image:        milvusImage,
		ExposedPorts: []string{milvusPort + "/tcp"},
		Env: map[string]string{
			"ETCD_USE_EMBED":            "true",
			"MINIO_USE_EMBED":           "true",
			"ROCKSMQ_USE_EMBED":         "true",
			"COMMON_STORAGE_TYPE":       "local",
			"DATA_PATH":                 "/var/lib/milvus/data",
			"PULSAR_ADDRESS":            "pulsar://localhost:6650",
			"ETCD_DATA_DIR":             "/var/lib/milvus/etcd",
			"ETCD_CONFIG_PATH":          "/var/lib/milvus/configs/etcd.yaml",
			"MINIO_ADDRESS":             "localhost:9000",
			"PULSAR_USE_EMBED":          "true",
			"STANDALONE_DEPLOY_MODE":    "true",
			"MILVUS_STANDALONE_ENABLED": "true",
		},
		WaitingFor: wait.ForListeningPort(milvusPort).WithStartupTimeout(120 * time.Second),
	}

	// 创建并启动容器
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	if err != nil {
		return nil, fmt.Errorf("无法启动Milvus测试容器: %w", err)
	}

	// 获取主机和端口信息
	host, err := container.Host(ctx)
	if err != nil {
		return nil, fmt.Errorf("无法获取Milvus容器主机: %w", err)
	}

	mappedPort, err := container.MappedPort(ctx, milvusPort+"/tcp")
	if err != nil {
		return nil, fmt.Errorf("无法获取Milvus容器端口映射: %w", err)
	}

	log.Printf("Milvus测试容器已启动: %s:%s", host, mappedPort.Port())

	return &MilvusContainer{
		container: container,
		host:      host,
		port:      mappedPort.Port(),
	}, nil
}

// Host 返回容器主机
func (mc *MilvusContainer) Host() string {
	return mc.host
}

// Port 返回容器端口
func (mc *MilvusContainer) Port() string {
	return mc.port
}

// Stop 停止并移除容器
func (mc *MilvusContainer) Stop(ctx context.Context) error {
	log.Println("正在停止Milvus测试容器...")
	return mc.container.Terminate(ctx)
}
