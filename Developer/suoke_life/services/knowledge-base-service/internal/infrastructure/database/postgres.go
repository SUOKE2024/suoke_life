package database

import (
	"context"
	"database/sql"
	"fmt"
	_ "github.com/lib/pq" // PostgreSQL驱动
)

// DBManager 数据库管理器接口
type DBManager interface {
	Exec(ctx context.Context, query string, args ...interface{}) (sql.Result, error)
	Query(ctx context.Context, query string, args ...interface{}) (Rows, error)
	QueryRow(ctx context.Context, query string, args ...interface{}) Row
	Begin(ctx context.Context) (Transaction, error)
	Close() error
}

// Row 表示单行查询结果的接口
type Row interface {
	Scan(dest ...interface{}) error
}

// Rows 表示多行查询结果的接口
type Rows interface {
	Next() bool
	Scan(dest ...interface{}) error
	Close() error
	Err() error
}

// Transaction 表示数据库事务的接口
type Transaction interface {
	Exec(query string, args ...interface{}) (sql.Result, error)
	Query(query string, args ...interface{}) (Rows, error)
	QueryRow(query string, args ...interface{}) Row
	Commit() error
	Rollback() error
}

// PostgresRow 包装 sql.Row 实现 Row 接口
type PostgresRow struct {
	row *sql.Row
}

// Scan 实现 Row 接口的 Scan 方法
func (r *PostgresRow) Scan(dest ...interface{}) error {
	return r.row.Scan(dest...)
}

// PostgresRows 包装 sql.Rows 实现 Rows 接口
type PostgresRows struct {
	rows *sql.Rows
}

// Next 实现 Rows 接口的 Next 方法
func (r *PostgresRows) Next() bool {
	return r.rows.Next()
}

// Scan 实现 Rows 接口的 Scan 方法
func (r *PostgresRows) Scan(dest ...interface{}) error {
	return r.rows.Scan(dest...)
}

// Close 实现 Rows 接口的 Close 方法
func (r *PostgresRows) Close() error {
	return r.rows.Close()
}

// Err 实现 Rows 接口的 Err 方法
func (r *PostgresRows) Err() error {
	return r.rows.Err()
}

// PostgresTransaction 包装 sql.Tx 实现 Transaction 接口
type PostgresTransaction struct {
	tx *sql.Tx
}

// Exec 实现 Transaction 接口的 Exec 方法
func (t *PostgresTransaction) Exec(query string, args ...interface{}) (sql.Result, error) {
	return t.tx.Exec(query, args...)
}

// Query 实现 Transaction 接口的 Query 方法
func (t *PostgresTransaction) Query(query string, args ...interface{}) (Rows, error) {
	rows, err := t.tx.Query(query, args...)
	if err != nil {
		return nil, err
	}
	return &PostgresRows{rows: rows}, nil
}

// QueryRow 实现 Transaction 接口的 QueryRow 方法
func (t *PostgresTransaction) QueryRow(query string, args ...interface{}) Row {
	return &PostgresRow{row: t.tx.QueryRow(query, args...)}
}

// Commit 实现 Transaction 接口的 Commit 方法
func (t *PostgresTransaction) Commit() error {
	return t.tx.Commit()
}

// Rollback 实现 Transaction 接口的 Rollback 方法
func (t *PostgresTransaction) Rollback() error {
	return t.tx.Rollback()
}

// PostgresDB PostgreSQL数据库连接
type PostgresDB struct {
	db *sql.DB
}

// NewPostgresDB 创建新的PostgreSQL连接
func NewPostgresDB(connStr string) (*PostgresDB, error) {
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, fmt.Errorf("打开数据库连接失败: %w", err)
	}

	// 测试连接
	if err := db.Ping(); err != nil {
		return nil, fmt.Errorf("数据库连接测试失败: %w", err)
	}

	return &PostgresDB{db: db}, nil
}

// Close 关闭数据库连接
func (p *PostgresDB) Close() error {
	return p.db.Close()
}

// Ping 检查数据库连接是否可用
func (p *PostgresDB) Ping(ctx context.Context) error {
	return p.db.PingContext(ctx)
}

// Exec 执行SQL语句
func (p *PostgresDB) Exec(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
	return p.db.ExecContext(ctx, query, args...)
}

// Query 执行查询
func (p *PostgresDB) Query(ctx context.Context, query string, args ...interface{}) (Rows, error) {
	rows, err := p.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	return &PostgresRows{rows: rows}, nil
}

// QueryRow 执行单行查询
func (p *PostgresDB) QueryRow(ctx context.Context, query string, args ...interface{}) Row {
	return &PostgresRow{row: p.db.QueryRowContext(ctx, query, args...)}
}

// Begin 开始事务
func (p *PostgresDB) Begin(ctx context.Context) (Transaction, error) {
	tx, err := p.db.BeginTx(ctx, nil)
	if err != nil {
		return nil, err
	}
	return &PostgresTransaction{tx: tx}, nil
}

// InitSchema 初始化数据库schema
func (p *PostgresDB) InitSchema() error {
	schema := `
    CREATE TABLE IF NOT EXISTS documents (
        id UUID PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        content_type TEXT NOT NULL,
        category_id UUID NOT NULL,
        author_id UUID NOT NULL,
        vector_id TEXT,
        tags TEXT[],
        blockchain_ref TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_documents_category_id ON documents(category_id);
    CREATE INDEX IF NOT EXISTS idx_documents_author_id ON documents(author_id);
    CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
    `

	_, err := p.db.Exec(schema)
	if err != nil {
		return fmt.Errorf("初始化数据库schema失败: %w", err)
	}

	return nil
}
