package di

import (
	"context"
	"fmt"
	
	"github.com/go-redis/redis/v8"
	"github.com/neo4j/neo4j-go-driver/v5/neo4j"
	"go.uber.org/zap"
	
	"knowledge-graph-service/internal/api/handlers"
	"knowledge-graph-service/internal/config"
	domainrepo "knowledge-graph-service/internal/domain/repositories"
	"knowledge-graph-service/internal/infrastructure/repositories"
	"knowledge-graph-service/internal/usecases"
)

// Container 依赖注入容器
type Container struct {
	// 基础配置
	Config *config.Config
	Logger *zap.Logger
	
	// 数据库连接
	Neo4jDriver neo4j.DriverWithContext
	RedisClient *redis.Client
	
	// 存储库
	NodeRepository         domainrepo.NodeRepository
	RelationshipRepository domainrepo.RelationshipRepository
	
	// 用例
	NodeUseCase         *usecases.NodeUseCase
	RelationshipUseCase *usecases.RelationshipUseCase
	GraphUseCase        *usecases.GraphUseCase
	
	// API处理程序
	NodeHandler         *handlers.NodeHandler
	RelationshipHandler *handlers.RelationshipHandler
	GraphHandler        *handlers.GraphHandler
}

// NewContainer 创建依赖注入容器
func NewContainer(cfg *config.Config, logger *zap.Logger) (*Container, error) {
	// 创建Neo4j驱动
	neo4jDriver, err := createNeo4jDriver(cfg, logger)
	if err != nil {
		return nil, fmt.Errorf("创建Neo4j驱动失败: %w", err)
	}
	
	// 创建Redis客户端
	redisClient, err := createRedisClient(cfg, logger)
	if err != nil {
		return nil, fmt.Errorf("创建Redis客户端失败: %w", err)
	}
	
	// 创建存储库
	nodeRepo := repositories.NewNeo4jNodeRepository(neo4jDriver, logger)
	relRepo := repositories.NewNeo4jRelationshipRepository(neo4jDriver, logger)
	
	// 创建用例
	nodeUseCase := usecases.NewNodeUseCase(nodeRepo, logger)
	relUseCase := usecases.NewRelationshipUseCase(relRepo, logger)
	graphUseCase := usecases.NewGraphUseCase(nodeRepo, relRepo, logger)
	
	// 创建容器
	container := &Container{
		Logger:             logger,
		Config:             cfg,
		Neo4jDriver:        neo4jDriver,
		RedisClient:        redisClient,
		NodeRepository:     nodeRepo,
		RelationshipRepository: relRepo,
		NodeUseCase:        nodeUseCase,
		RelationshipUseCase: relUseCase,
		GraphUseCase:       graphUseCase,
	}
	
	// 初始化API处理程序
	container.NodeHandler = handlers.NewNodeHandler(nodeUseCase)
	container.RelationshipHandler = handlers.NewRelationshipHandler(relUseCase)
	container.GraphHandler = handlers.NewGraphHandler(graphUseCase)
	
	return container, nil
}

// Close 关闭所有连接
func (c *Container) Close(ctx context.Context) error {
	if c.Neo4jDriver != nil {
		if err := c.Neo4jDriver.Close(ctx); err != nil {
			c.Logger.Error("关闭Neo4j驱动失败", zap.Error(err))
		}
	}
	
	if c.RedisClient != nil {
		if err := c.RedisClient.Close(); err != nil {
			c.Logger.Error("关闭Redis客户端失败", zap.Error(err))
		}
	}
	
	return nil
}

// 创建Neo4j驱动
func createNeo4jDriver(cfg *config.Config, logger *zap.Logger) (neo4j.DriverWithContext, error) {
	driver, err := neo4j.NewDriverWithContext(
		cfg.Neo4j.URI,
		neo4j.BasicAuth(cfg.Neo4j.Username, cfg.Neo4j.Password, ""),
		func(config *neo4j.Config) {
			config.MaxConnectionPoolSize = cfg.Neo4j.MaxConn
		},
	)
	if err != nil {
		return nil, err
	}
	
	// 验证连接
	ctx := context.Background()
	if err := driver.VerifyConnectivity(ctx); err != nil {
		return nil, err
	}
	
	logger.Info("成功连接Neo4j数据库", zap.String("uri", cfg.Neo4j.URI))
	return driver, nil
}

// 创建Redis客户端
func createRedisClient(cfg *config.Config, logger *zap.Logger) (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     fmt.Sprintf("%s:%d", cfg.Redis.Host, cfg.Redis.Port),
		Password: cfg.Redis.Password,
		DB:       cfg.Redis.DB,
		PoolSize: cfg.Redis.PoolSize,
	})
	
	// 验证连接
	ctx := context.Background()
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, err
	}
	
	logger.Info("成功连接Redis数据库", zap.String("host", cfg.Redis.Host), zap.Int("port", cfg.Redis.Port))
	return client, nil
}