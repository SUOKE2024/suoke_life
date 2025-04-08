package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"

	"knowledge-base-service/internal/domain/entity"
	"knowledge-base-service/internal/domain/repository"
	"knowledge-base-service/internal/infrastructure/database"
	"knowledge-base-service/internal/infrastructure/vectorstore"
)

// PostgresDocumentRepository 基于PostgreSQL的文档存储库实现
type PostgresDocumentRepository struct {
	db          database.DBManager
	vectorStore *vectorstore.MilvusClient
	blockchain  BlockchainClient
}

// BlockchainClient 区块链客户端接口
type BlockchainClient interface {
	RegisterDocument(ctx context.Context, doc *entity.Document) (string, error)
	VerifyDocument(ctx context.Context, doc *entity.Document) (bool, error)
}

// NewPostgresDocumentRepository 创建PostgreSQL文档存储库
func NewPostgresDocumentRepository(
	db database.DBManager,
	vectorStore *vectorstore.MilvusClient,
	blockchain BlockchainClient,
) repository.DocumentRepository {
	return &PostgresDocumentRepository{
		db:          db,
		vectorStore: vectorStore,
		blockchain:  blockchain,
	}
}

// FindByID 通过ID查找文档
func (r *PostgresDocumentRepository) FindByID(ctx context.Context, id uuid.UUID) (*entity.Document, error) {
	query := `
        SELECT 
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at
        FROM documents 
        WHERE id = $1 AND status != $2
    `

	row := r.db.QueryRow(ctx, query, id, entity.StatusDeleted)

	doc, err := r.scanDocument(row)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("查询文档失败: %w", err)
	}

	// 加载文档块
	chunks, err := r.findChunks(ctx, id)
	if err != nil {
		return nil, err
	}

	doc.Chunks = chunks

	return doc, nil
}

// FindByCategory 查找分类下的所有文档
func (r *PostgresDocumentRepository) FindByCategory(ctx context.Context, categoryID uuid.UUID) ([]*entity.Document, error) {
	query := `
        SELECT 
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at
        FROM documents 
        WHERE category_id = $1 AND status != $2
        ORDER BY created_at DESC
    `

	rows, err := r.db.Query(ctx, query, categoryID, entity.StatusDeleted)
	if err != nil {
		return nil, fmt.Errorf("查询分类文档失败: %w", err)
	}
	defer rows.Close()

	return r.scanDocuments(ctx, rows)
}

// FindByTags 通过标签查找文档
func (r *PostgresDocumentRepository) FindByTags(ctx context.Context, tags []string) ([]*entity.Document, error) {
	if len(tags) == 0 {
		return []*entity.Document{}, nil
	}

	// 构建查询
	query := `
        SELECT 
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at
        FROM documents 
        WHERE status != $1 AND tags @> $2
        ORDER BY created_at DESC
    `

	// 将标签数组转换为PostgreSQL数组
	tagsJson, err := json.Marshal(tags)
	if err != nil {
		return nil, fmt.Errorf("转换标签失败: %w", err)
	}

	rows, err := r.db.Query(ctx, query, entity.StatusDeleted, tagsJson)
	if err != nil {
		return nil, fmt.Errorf("查询标签文档失败: %w", err)
	}
	defer rows.Close()

	return r.scanDocuments(ctx, rows)
}

// Search 全文搜索
func (r *PostgresDocumentRepository) Search(ctx context.Context, query string) ([]*entity.Document, error) {
	if query == "" {
		return []*entity.Document{}, nil
	}

	// 使用PostgreSQL的全文搜索功能
	searchQuery := `
        SELECT 
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at,
            ts_rank(to_tsvector('chinese', title || ' ' || description || ' ' || content), 
                    plainto_tsquery('chinese', $1)) AS rank
        FROM documents 
        WHERE status != $2 
          AND to_tsvector('chinese', title || ' ' || description || ' ' || content) @@ 
              plainto_tsquery('chinese', $1)
        ORDER BY rank DESC
    `

	rows, err := r.db.Query(ctx, searchQuery, query, entity.StatusDeleted)
	if err != nil {
		return nil, fmt.Errorf("全文搜索失败: %w", err)
	}
	defer rows.Close()

	return r.scanDocuments(ctx, rows)
}

// SemanticSearch 语义搜索
func (r *PostgresDocumentRepository) SemanticSearch(ctx context.Context, query string, limit int) ([]*entity.Document, error) {
	if query == "" {
		return []*entity.Document{}, nil
	}

	// 这里需要调用外部服务获取查询的向量表示
	queryVector, err := r.getQueryVector(ctx, query)
	if err != nil {
		return nil, err
	}

	// 使用向量存储搜索相似向量
	docIDs, _, err := r.vectorStore.SearchVector(ctx, queryVector, limit)
	if err != nil {
		return nil, fmt.Errorf("向量搜索失败: %w", err)
	}

	if len(docIDs) == 0 {
		return []*entity.Document{}, nil
	}

	// 获取文档ID
	documentIDSet := make(map[string]bool)
	for _, id := range docIDs {
		documentIDSet[id] = true
	}

	// 构建IN查询的ID列表
	idList := make([]string, 0, len(documentIDSet))
	uuidList := make([]uuid.UUID, 0, len(documentIDSet))

	for id := range documentIDSet {
		idList = append(idList, id)

		// 解析UUID
		docUUID, err := uuid.Parse(id)
		if err == nil {
			uuidList = append(uuidList, docUUID)
		}
	}

	// 查询文档
	placeholders := make([]string, len(uuidList))
	args := make([]interface{}, len(uuidList)+1)

	args[0] = entity.StatusDeleted

	for i, id := range uuidList {
		placeholders[i] = fmt.Sprintf("$%d", i+2)
		args[i+1] = id
	}

	query = fmt.Sprintf(`
        SELECT 
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at
        FROM documents 
        WHERE status != $1 AND id IN (%s)
    `, strings.Join(placeholders, ", "))

	rows, err := r.db.Query(ctx, query, args...)
	if err != nil {
		return nil, fmt.Errorf("查询文档失败: %w", err)
	}
	defer rows.Close()

	return r.scanDocuments(ctx, rows)
}

// Save 保存文档
func (r *PostgresDocumentRepository) Save(ctx context.Context, document *entity.Document) error {
	// 开始事务
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return fmt.Errorf("开始事务失败: %w", err)
	}
	defer tx.Rollback()

	// 存储文档
	tagsJson, err := json.Marshal(document.Tags)
	if err != nil {
		return fmt.Errorf("序列化标签失败: %w", err)
	}

	metadataJson, err := json.Marshal(document.Metadata)
	if err != nil {
		return fmt.Errorf("序列化元数据失败: %w", err)
	}

	query := `
        INSERT INTO documents (
            id, title, description, content, content_type, status, 
            author_id, category_id, tags, tx_hash, metadata, 
            created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
        )
    `

	_, err = tx.Exec(query,
		document.ID,
		document.Title,
		document.Description,
		document.Content,
		document.ContentType,
		document.Status,
		document.AuthorID,
		document.CategoryID,
		tagsJson,
		document.TxHash,
		metadataJson,
		document.CreatedAt,
		document.UpdatedAt,
	)

	if err != nil {
		return fmt.Errorf("插入文档失败: %w", err)
	}

	// 存储文档块
	if len(document.Chunks) > 0 {
		err = r.saveChunks(ctx, tx, document.Chunks)
		if err != nil {
			return err
		}
	}

	// 提交事务
	err = tx.Commit()
	if err != nil {
		return fmt.Errorf("提交事务失败: %w", err)
	}

	return nil
}

// Update 更新文档
func (r *PostgresDocumentRepository) Update(ctx context.Context, document *entity.Document) error {
	// 开始事务
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return fmt.Errorf("开始事务失败: %w", err)
	}
	defer tx.Rollback()

	// 更新文档
	tagsJson, err := json.Marshal(document.Tags)
	if err != nil {
		return fmt.Errorf("序列化标签失败: %w", err)
	}

	metadataJson, err := json.Marshal(document.Metadata)
	if err != nil {
		return fmt.Errorf("序列化元数据失败: %w", err)
	}

	query := `
        UPDATE documents SET
            title = $1,
            description = $2,
            content = $3,
            content_type = $4,
            status = $5,
            category_id = $6,
            tags = $7,
            tx_hash = $8,
            metadata = $9,
            updated_at = $10
        WHERE id = $11
    `

	_, err = tx.Exec(query,
		document.Title,
		document.Description,
		document.Content,
		document.ContentType,
		document.Status,
		document.CategoryID,
		tagsJson,
		document.TxHash,
		metadataJson,
		document.UpdatedAt,
		document.ID,
	)

	if err != nil {
		return fmt.Errorf("更新文档失败: %w", err)
	}

	// 删除现有块
	_, err = tx.Exec("DELETE FROM document_chunks WHERE document_id = $1", document.ID)
	if err != nil {
		return fmt.Errorf("删除文档块失败: %w", err)
	}

	// 保存新块
	if len(document.Chunks) > 0 {
		err = r.saveChunks(ctx, tx, document.Chunks)
		if err != nil {
			return err
		}
	}

	// 提交事务
	err = tx.Commit()
	if err != nil {
		return fmt.Errorf("提交事务失败: %w", err)
	}

	return nil
}

// Delete 删除文档
func (r *PostgresDocumentRepository) Delete(ctx context.Context, id uuid.UUID) error {
	// 将文档标记为已删除，而不是物理删除
	query := `
        UPDATE documents SET
            status = $1,
            updated_at = $2
        WHERE id = $3
    `

	_, err := r.db.Exec(ctx, query, entity.StatusDeleted, time.Now(), id)
	if err != nil {
		return fmt.Errorf("删除文档失败: %w", err)
	}

	// 删除向量存储中的向量
	idStr := id.String()
	err = r.vectorStore.DeleteVector(ctx, idStr)
	if err != nil {
		// 仅记录错误，不中断流程
		fmt.Printf("删除向量失败: %v\n", err)
	}

	return nil
}

// RegisterOnBlockchain 在区块链上注册文档
func (r *PostgresDocumentRepository) RegisterOnBlockchain(ctx context.Context, document *entity.Document) (string, error) {
	if document.IsRegisteredOnBlockchain() {
		return document.TxHash, nil
	}

	// 调用区块链服务注册文档
	txHash, err := r.blockchain.RegisterDocument(ctx, document)
	if err != nil {
		return "", fmt.Errorf("区块链注册失败: %w", err)
	}

	// 更新文档的交易哈希
	document.SetBlockchainTxHash(txHash)

	// 更新数据库中的交易哈希
	query := `
        UPDATE documents SET
            tx_hash = $1,
            updated_at = $2
        WHERE id = $3
    `

	_, err = r.db.Exec(ctx, query, txHash, document.UpdatedAt, document.ID)
	if err != nil {
		return txHash, fmt.Errorf("更新交易哈希失败: %w", err)
	}

	return txHash, nil
}

// 扫描单个文档
func (r *PostgresDocumentRepository) scanDocument(row database.Row) (*entity.Document, error) {
	var doc entity.Document
	var tagsJson, metadataJson []byte
	var contentTypeStr, statusStr string

	err := row.Scan(
		&doc.ID,
		&doc.Title,
		&doc.Description,
		&doc.Content,
		&contentTypeStr,
		&statusStr,
		&doc.AuthorID,
		&doc.CategoryID,
		&tagsJson,
		&doc.TxHash,
		&metadataJson,
		&doc.CreatedAt,
		&doc.UpdatedAt,
	)

	if err != nil {
		return nil, err
	}

	// 解析内容类型和状态
	doc.ContentType = entity.ContentType(contentTypeStr)
	doc.Status = entity.DocumentStatus(statusStr)

	// 解析标签
	if err := json.Unmarshal(tagsJson, &doc.Tags); err != nil {
		return nil, fmt.Errorf("解析标签失败: %w", err)
	}

	// 解析元数据
	if err := json.Unmarshal(metadataJson, &doc.Metadata); err != nil {
		return nil, fmt.Errorf("解析元数据失败: %w", err)
	}

	return &doc, nil
}

// 扫描多个文档
func (r *PostgresDocumentRepository) scanDocuments(ctx context.Context, rows database.Rows) ([]*entity.Document, error) {
	var documents []*entity.Document

	for rows.Next() {
		doc, err := r.scanDocument(rows)
		if err != nil {
			return nil, err
		}

		documents = append(documents, doc)
	}

	if rows.Err() != nil {
		return nil, rows.Err()
	}

	// 如果有文档，加载它们的块
	if len(documents) > 0 {
		for _, doc := range documents {
			chunks, err := r.findChunks(ctx, doc.ID)
			if err != nil {
				return nil, err
			}
			doc.Chunks = chunks
		}
	}

	return documents, nil
}

// 查找文档块
func (r *PostgresDocumentRepository) findChunks(ctx context.Context, documentID uuid.UUID) ([]entity.Chunk, error) {
	query := `
        SELECT 
            id, document_id, content, vector_id, metadata, 
            token_count, offset, length, created_at
        FROM document_chunks 
        WHERE document_id = $1
        ORDER BY offset ASC
    `

	rows, err := r.db.Query(ctx, query, documentID)
	if err != nil {
		return nil, fmt.Errorf("查询文档块失败: %w", err)
	}
	defer rows.Close()

	var chunks []entity.Chunk

	for rows.Next() {
		var chunk entity.Chunk
		var metadataJson []byte

		err := rows.Scan(
			&chunk.ID,
			&chunk.DocumentID,
			&chunk.Content,
			&chunk.VectorID,
			&metadataJson,
			&chunk.TokenCount,
			&chunk.Offset,
			&chunk.Length,
			&chunk.CreatedAt,
		)

		if err != nil {
			return nil, err
		}

		// 解析元数据
		if err := json.Unmarshal(metadataJson, &chunk.Metadata); err != nil {
			return nil, fmt.Errorf("解析块元数据失败: %w", err)
		}

		chunks = append(chunks, chunk)
	}

	if rows.Err() != nil {
		return nil, rows.Err()
	}

	return chunks, nil
}

// 保存文档块
func (r *PostgresDocumentRepository) saveChunks(ctx context.Context, tx database.Transaction, chunks []entity.Chunk) error {
	query := `
        INSERT INTO document_chunks (
            id, document_id, content, vector_id, metadata,
            token_count, offset, length, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9
        )
    `

	for _, chunk := range chunks {
		metadataJson, err := json.Marshal(chunk.Metadata)
		if err != nil {
			return fmt.Errorf("序列化块元数据失败: %w", err)
		}

		_, err = tx.Exec(query,
			chunk.ID,
			chunk.DocumentID,
			chunk.Content,
			chunk.VectorID,
			metadataJson,
			chunk.TokenCount,
			chunk.Offset,
			chunk.Length,
			chunk.CreatedAt,
		)

		if err != nil {
			return fmt.Errorf("插入文档块失败: %w", err)
		}
	}

	return nil
}

// 获取查询向量
func (r *PostgresDocumentRepository) getQueryVector(ctx context.Context, query string) ([]float32, error) {
	// 这里应该调用嵌入式模型获取查询向量
	// 为简化示例，返回模拟的向量
	vector := make([]float32, 1536)
	for i := range vector {
		vector[i] = 0.1 // 示例值
	}
	return vector, nil
}
