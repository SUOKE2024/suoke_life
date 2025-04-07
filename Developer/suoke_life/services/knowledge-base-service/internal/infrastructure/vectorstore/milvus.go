package vectorstore

import (
    "context"
    "fmt"
    "time"
    "github.com/google/uuid"
    
    "github.com/milvus-io/milvus-sdk-go/v2/client"
    "github.com/milvus-io/milvus-sdk-go/v2/entity"
)

const (
    // 集合名称 - 默认值，可以被覆盖
    defaultCollectionName = "documents"
    
    // 向量维度
    vectorDimension = 1536 // 使用OpenAI ada-002模型的默认维度
    
    // 索引类型
    indexType = "IVF_FLAT"
    
    // 检索参数
    searchTopK = 10
)

// MilvusClient Milvus向量数据库客户端
type MilvusClient struct {
    client client.Client
    collectionName string
}

// NewMilvusClient 创建新的Milvus客户端
func NewMilvusClient(host string, port int) (*MilvusClient, error) {
    address := fmt.Sprintf("%s:%d", host, port)
    return NewMilvusClientWithAddr(address)
}

// NewMilvusClientWithAddr 创建新的Milvus客户端（使用完整地址）
func NewMilvusClientWithAddr(address string) (*MilvusClient, error) {
    // 连接Milvus
    c, err := client.NewGrpcClient(context.Background(), address)
    if err != nil {
        return nil, fmt.Errorf("连接Milvus失败: %w", err)
    }
    
    m := &MilvusClient{
        client: c,
        collectionName: defaultCollectionName,
    }
    
    // 确保集合存在
    if err := m.ensureCollection(); err != nil {
        return nil, err
    }
    
    return m, nil
}

// SetCollectionName 设置集合名称
func (m *MilvusClient) SetCollectionName(name string) {
    m.collectionName = name
}

// Close 关闭Milvus连接
func (m *MilvusClient) Close() error {
    return m.client.Close()
}

// 确保集合存在
func (m *MilvusClient) ensureCollection() error {
    ctx := context.Background()
    
    // 检查集合是否存在
    has, err := m.client.HasCollection(ctx, m.collectionName)
    if err != nil {
        return fmt.Errorf("检查集合是否存在失败: %w", err)
    }
    
    // 如果集合不存在，创建新集合
    if !has {
        schema := &entity.Schema{
            CollectionName: m.collectionName,
            Description:    "文档向量存储",
            Fields: []*entity.Field{
                {
                    Name:       "id",
                    DataType:   entity.FieldTypeVarChar,
                    PrimaryKey: true,
                    AutoID:     false,
                    TypeParams: map[string]string{
                        "max_length": "36", // UUID长度
                    },
                },
                {
                    Name:     "vector",
                    DataType: entity.FieldTypeFloatVector,
                    TypeParams: map[string]string{
                        "dim": fmt.Sprintf("%d", vectorDimension),
                    },
                },
                {
                    Name:       "document_id",
                    DataType:   entity.FieldTypeVarChar,
                    PrimaryKey: false,
                    AutoID:     false,
                    TypeParams: map[string]string{
                        "max_length": "36", // UUID长度
                    },
                },
                {
                    Name:     "created_at",
                    DataType: entity.FieldTypeInt64,
                },
            },
        }
        
        err = m.client.CreateCollection(ctx, schema, 1)
        if err != nil {
            return fmt.Errorf("创建集合失败: %w", err)
        }
        
        // 创建索引
        idx, err := entity.NewIndexIvfFlat(entity.L2, 256)
        if err != nil {
            return fmt.Errorf("创建索引配置失败: %w", err)
        }
        
        err = m.client.CreateIndex(ctx, m.collectionName, "vector", idx, false)
        if err != nil {
            return fmt.Errorf("创建索引失败: %w", err)
        }
    }
    
    // 加载集合
    err = m.client.LoadCollection(ctx, m.collectionName, false)
    if err != nil {
        return fmt.Errorf("加载集合失败: %w", err)
    }
    
    return nil
}

// StoreVector 存储向量
func (m *MilvusClient) StoreVector(ctx context.Context, docID string, vector []float32) (string, error) {
    // 生成唯一ID
    id := uuid.New().String()
    
    // 准备数据列
    idColumn := entity.NewColumnVarChar("id", []string{id})
    docColumn := entity.NewColumnVarChar("document_id", []string{docID})
    vectorColumn := entity.NewColumnFloatVector("vector", vectorDimension, [][]float32{vector})
    timestampColumn := entity.NewColumnInt64("created_at", []int64{time.Now().UnixNano() / 1e6})
    
    // 插入数据
    _, err := m.client.Insert(
        ctx,
        m.collectionName,
        "",
        idColumn,
        docColumn,
        vectorColumn,
        timestampColumn,
    )
    
    if err != nil {
        return "", fmt.Errorf("向量存储失败: %w", err)
    }
    
    return id, nil
}

// SearchVector 搜索向量
func (m *MilvusClient) SearchVector(ctx context.Context, vector []float32, limit int) ([]string, []float32, error) {
    // 搜索参数
    sp, err := entity.NewIndexIvfFlatSearchParam(16)
    if err != nil {
        return nil, nil, fmt.Errorf("创建搜索参数失败: %w", err)
    }
    
    // 准备搜索向量
    vectors := []entity.Vector{entity.FloatVector(vector)}
    
    // 执行搜索
    results, err := m.client.Search(
        ctx,
        m.collectionName,
        []string{},
        "",
        []string{"document_id"},
        vectors,
        "vector",
        entity.L2,
        limit,
        sp,
    )
    
    if err != nil {
        return nil, nil, fmt.Errorf("向量搜索失败: %w", err)
    }
    
    // 解析结果
    documentIDs := make([]string, 0, limit)
    scores := make([]float32, 0, limit)
    
    for _, result := range results {
        for i, id := range result.IDs.(*entity.ColumnVarChar).Data() {
            documentIDs = append(documentIDs, id)
            scores = append(scores, result.Scores[i])
        }
    }
    
    return documentIDs, scores, nil
}

// DeleteVector 删除向量
func (m *MilvusClient) DeleteVector(ctx context.Context, vectorID string) error {
    expr := fmt.Sprintf("id == \"%s\"", vectorID)
    err := m.client.Delete(
        ctx,
        m.collectionName,
        expr,
        "", // 分区名称，如果不使用分区则为空字符串
    )
    
    if err != nil {
        return fmt.Errorf("删除向量失败: %w", err)
    }
    
    return nil
}