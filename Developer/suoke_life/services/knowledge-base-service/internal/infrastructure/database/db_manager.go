package database

import (
    "context"
    "database/sql"
)

// DBManagerImpl 实现 DBManager 接口
type DBManagerImpl struct {
    db *sql.DB
}

// NewDBManager 创建数据库管理器
func NewDBManager(db *sql.DB) DBManager {
    return &DBManagerImpl{db: db}
}

// Exec 执行 SQL 语句
func (m *DBManagerImpl) Exec(ctx context.Context, query string, args ...interface{}) (sql.Result, error) {
    return m.db.ExecContext(ctx, query, args...)
}

// Query 执行查询
func (m *DBManagerImpl) Query(ctx context.Context, query string, args ...interface{}) (Rows, error) {
    rows, err := m.db.QueryContext(ctx, query, args...)
    if err != nil {
        return nil, err
    }
    return &PostgresRows{rows: rows}, nil
}

// QueryRow 执行单行查询
func (m *DBManagerImpl) QueryRow(ctx context.Context, query string, args ...interface{}) Row {
    return &PostgresRow{row: m.db.QueryRowContext(ctx, query, args...)}
}

// Begin 开始事务
func (m *DBManagerImpl) Begin(ctx context.Context) (Transaction, error) {
    tx, err := m.db.BeginTx(ctx, nil)
    if err != nil {
        return nil, err
    }
    return &PostgresTransaction{tx: tx}, nil
}

// Close 关闭数据库连接
func (m *DBManagerImpl) Close() error {
    return m.db.Close()
} 