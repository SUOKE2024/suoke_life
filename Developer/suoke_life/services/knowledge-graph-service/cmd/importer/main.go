package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"

	"knowledge-graph-service/cmd/importer/mocks"
	"knowledge-graph-service/internal/domain/repositories"
	"knowledge-graph-service/internal/importer"
	"knowledge-graph-service/internal/importer/parsers"
)

var (
	sourcePath   string
	importType   string
	format       string
	dryRun       bool
	logLevel     string
	outputFormat string
	jsonPath     string
	xmlRecordElem string
)

func init() {
	flag.StringVar(&sourcePath, "source", "", "数据源文件路径")
	flag.StringVar(&importType, "type", "", "导入类型 (herbs, formulas)")
	flag.StringVar(&format, "format", "", "数据格式 (auto, csv, json, xml)，默认自动检测")
	flag.BoolVar(&dryRun, "dry-run", false, "仅测试，不写入数据库")
	flag.StringVar(&logLevel, "log-level", "info", "日志级别 (debug, info, warn, error)")
	flag.StringVar(&outputFormat, "output", "console", "输出格式 (console, json)")
	flag.StringVar(&jsonPath, "json-path", "", "JSON数据路径，如 data.items")
	flag.StringVar(&xmlRecordElem, "xml-record", "", "XML记录元素名称")
}

func main() {
	flag.Parse()

	// 初始化日志
	logger := initLogger(logLevel, outputFormat)
	defer logger.Sync()

	if sourcePath == "" || importType == "" {
		logger.Fatal("必须指定数据源文件路径和导入类型",
			zap.String("source", sourcePath),
			zap.String("type", importType),
		)
	}

	// 检查源文件是否存在
	if _, err := os.Stat(sourcePath); os.IsNotExist(err) {
		logger.Fatal("数据源文件不存在", zap.String("source", sourcePath))
	}

	// 创建存储库
	var nodeRepo repositories.NodeRepository
	var relRepo repositories.RelationshipRepository
	
	// 使用mock存储库
	logger.Info("使用模拟存储库模式")
	nodeRepo = mocks.NewSimpleNodeRepository(logger)
	relRepo = mocks.NewSimpleRelationshipRepository(logger)

	// 创建上下文
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Minute)
	defer cancel()

	// 根据类型导入数据
	var err error
	startTime := time.Now()
	
	switch importType {
	case "herbs":
		err = importHerbs(ctx, sourcePath, nodeRepo, relRepo, logger)
	case "formulas":
		err = importFormulas(ctx, sourcePath, nodeRepo, relRepo, logger)
	default:
		logger.Fatal("不支持的导入类型", zap.String("type", importType))
	}

	if err != nil {
		logger.Fatal("导入失败", zap.Error(err))
	}

	duration := time.Since(startTime)
	logger.Info("导入完成", zap.Duration("duration", duration))
}

// 导入中药数据
func importHerbs(ctx context.Context, filePath string, nodeRepo repositories.NodeRepository, relRepo repositories.RelationshipRepository, logger *zap.Logger) error {
	// 创建解析器工厂
	parserFactory := parsers.NewParserFactory(logger)
	
	// 创建适合的解析器
	var parser parsers.Parser
	var err error
	
	if format == "" || format == "auto" {
		// 自动检测数据格式
		parser, err = parserFactory.CreateParser(filePath, nil)
	} else {
		// 使用指定的格式
		var options parsers.ParseOptions
		
		switch strings.ToLower(format) {
		case "csv":
			options = parsers.DefaultCSVParseOptions()
		case "json":
			jsonOptions := parsers.DefaultJSONParseOptions()
			if jsonPath != "" {
				jsonOptions.RootArrayPath = jsonPath
			}
			options = jsonOptions
		case "xml":
			xmlOptions := parsers.DefaultXMLParseOptions()
			if xmlRecordElem != "" {
				xmlOptions.RecordElement = xmlRecordElem
			}
			options = xmlOptions
		default:
			return fmt.Errorf("不支持的数据格式: %s", format)
		}
		
		parser, err = parserFactory.CreateParser(filePath, options)
	}
	
	if err != nil {
		return fmt.Errorf("创建解析器失败: %w", err)
	}
	
	// 解析数据
	if err := parser.Parse(); err != nil {
		return fmt.Errorf("解析文件失败: %w", err)
	}
	
	// 获取数据
	rows, err := parser.GetRowsAsMap()
	if err != nil {
		return fmt.Errorf("获取数据失败: %w", err)
	}
	
	// 创建中药导入器
	herbImporter := importer.NewHerbImporter(
		nodeRepo,
		relRepo,
		logger,
		importer.DefaultHerbFields(),
	)
	
	// 设置导入选项
	options := importer.DefaultImportOptions()
	options.BatchSize = 10
	options.CreateRelations = true
	
	// 准备导入数据
	importSource := filepath.Base(filePath) // 使用文件名作为源标识
	
	// 创建自定义导入方法，使用已解析的数据
	customImport := func() (importer.ImportStats, error) {
		return herbImporter.ImportFromData(ctx, rows, importSource, options)
	}
	
	// 执行导入
	stats, err := customImport()
	if err != nil {
		logger.Error("中药导入失败", zap.Error(err))
		return err
	}
	
	// 输出导入统计
	logger.Info("导入统计",
		zap.Int("total", stats.TotalCount),
		zap.Int("success", stats.SuccessCount),
		zap.Int("failed", stats.FailedCount))
	
	return nil
}

// 导入方剂数据
func importFormulas(ctx context.Context, filePath string, nodeRepo repositories.NodeRepository, relRepo repositories.RelationshipRepository, logger *zap.Logger) error {
	// 创建解析器工厂
	parserFactory := parsers.NewParserFactory(logger)
	
	// 创建适合的解析器
	var parser parsers.Parser
	var err error
	
	if format == "" || format == "auto" {
		// 自动检测数据格式
		parser, err = parserFactory.CreateParser(filePath, nil)
	} else {
		// 使用指定的格式
		var options parsers.ParseOptions
		
		switch strings.ToLower(format) {
		case "csv":
			options = parsers.DefaultCSVParseOptions()
		case "json":
			jsonOptions := parsers.DefaultJSONParseOptions()
			if jsonPath != "" {
				jsonOptions.RootArrayPath = jsonPath
			}
			options = jsonOptions
		case "xml":
			xmlOptions := parsers.DefaultXMLParseOptions()
			if xmlRecordElem != "" {
				xmlOptions.RecordElement = xmlRecordElem
			}
			options = xmlOptions
		default:
			return fmt.Errorf("不支持的数据格式: %s", format)
		}
		
		parser, err = parserFactory.CreateParser(filePath, options)
	}
	
	if err != nil {
		return fmt.Errorf("创建解析器失败: %w", err)
	}
	
	// 解析数据
	if err := parser.Parse(); err != nil {
		return fmt.Errorf("解析文件失败: %w", err)
	}
	
	// 获取数据
	rows, err := parser.GetRowsAsMap()
	if err != nil {
		return fmt.Errorf("获取数据失败: %w", err)
	}
	
	// 使用FormulaCSVImporter导入方剂数据
	logger.Info("开始导入方剂数据", zap.String("filePath", filePath))
	
	// 创建方剂导入器
	fieldMapping := importer.DefaultFormulaFields()
	formulaImporter := importer.NewFormulaImporter(nodeRepo, relRepo, logger, fieldMapping)
	
	// 设置导入选项
	options := importer.DefaultImportOptions()
	options.BatchSize = 10
	options.CreateRelations = true
	
	// 准备导入数据
	importSource := filepath.Base(filePath) // 使用文件名作为源标识
	
	// 创建自定义导入方法，使用已解析的数据
	customImport := func() (importer.ImportStats, error) {
		return formulaImporter.ImportFromData(ctx, rows, importSource, options)
	}
	
	// 执行导入
	stats, err := customImport()
	if err != nil {
		logger.Error("方剂导入失败", zap.Error(err))
		return err
	}
	
	// 输出导入统计
	logger.Info("方剂导入统计",
		zap.Int("total", stats.TotalCount),
		zap.Int("success", stats.SuccessCount),
		zap.Int("failed", stats.FailedCount),
		zap.Int("nodes", stats.NodesCreated),
		zap.Int("relationships", stats.RelsCreated),
		zap.Int("warnings", len(stats.Warnings)),
		zap.Int("errors", len(stats.Errors)))
	
	return nil
}

// 初始化日志记录器
func initLogger(level, format string) *zap.Logger {
	var levelEnum zapcore.Level
	switch level {
	case "debug":
		levelEnum = zapcore.DebugLevel
	case "info":
		levelEnum = zapcore.InfoLevel
	case "warn":
		levelEnum = zapcore.WarnLevel
	case "error":
		levelEnum = zapcore.ErrorLevel
	default:
		levelEnum = zapcore.InfoLevel
	}

	var config zap.Config
	if format == "json" {
		config = zap.NewProductionConfig()
	} else {
		config = zap.NewDevelopmentConfig()
	}
	config.Level = zap.NewAtomicLevelAt(levelEnum)

	logger, err := config.Build()
	if err != nil {
		fmt.Printf("初始化日志失败: %v\n", err)
		os.Exit(1)
	}

	return logger
}