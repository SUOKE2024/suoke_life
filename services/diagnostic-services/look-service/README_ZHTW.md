# 望診服務 (Look Service)

望診服務是索克生活APP的核心微服務之一，負責提供基於中醫望診理論的面色分析和形體分析功能。透過多模態視覺分析技術，將用戶的面部特徵和體態特徵與中醫理論相結合，提供個性化的健康分析和建議。

## 功能特點

- **面色分析**：分析用戶面部圖像的色澤、光澤和水分狀態，將其與中醫五色（青、赤、黃、白、黑）理論相關聯，推斷臟腑功能狀態。
- **形體分析**：分析用戶體態，包括體型特徵、姿態和比例，評估氣血運行、臟腑功能以及整體健康狀態。
- **舌象分析**：分析舌頭圖像，包括舌質、舌苔的色澤與分布，評估內臟功能狀態。
- **中醫理論關聯**：將視覺特徵與中醫理論關聯，生成體質分析和健康建議。
- **數據持久化**：保存分析記錄，支持歷史查詢和趨勢分析。
- **小艾服務集成**：與小艾服務(xiaoai-service)集成，提供更全面的中醫四診分析結果。

## 技術架構

- **程式語言**：Python 3.11
- **通訊協議**：gRPC
- **圖像處理**：OpenCV, NumPy
- **人工智能**：計算機視覺與傳統中醫知識圖譜結合
- **存儲**：SQLite（輕量級文件數據庫）
- **監控**：Prometheus, OpenTelemetry
- **部署**：Docker, Kubernetes

## 項目結構

```
look-service/
├── api/                    # API定義
│   └── grpc/               # gRPC協議定義
│       ├── look_service.proto  # 服務協議定義
│       └── ...
├── cmd/                    # 命令行工具和服務入口
│   └── server.py           # 服務入口
├── config/                 # 配置相關
│   ├── config.py           # 配置加載
│   └── config.yaml         # 配置文件
├── deploy/                 # 部署相關
│   ├── docker/             # Docker部署
│   └── kubernetes/         # Kubernetes部署
├── internal/               # 內部實現
│   ├── analysis/           # 分析算法
│   │   ├── face_analyzer.py   # 面色分析器
│   │   └── body_analyzer.py   # 形體分析器
│   ├── delivery/           # 服務實現
│   │   └── look_service_impl.py  # 服務實現
│   ├── integration/        # 外部集成
│   │   └── xiaoai_client.py     # 小艾服務客戶端
│   ├── model/              # 模型相關
│   │   └── model_factory.py    # 模型工廠
│   └── repository/         # 數據存儲
│       └── analysis_repository.py  # 分析結果存儲
├── pkg/                    # 通用工具包
│   └── utils/              # 工具類
│       ├── exceptions.py   # 異常定義
│       └── image_utils.py  # 圖像處理工具
├── test/                   # 測試
│   ├── integration/        # 集成測試
│   ├── performance/        # 性能測試
│   └── unit/               # 單元測試
├── Dockerfile              # Docker構建文件
├── README.md               # 項目說明
└── requirements.txt        # 依賴項
```

## 快速開始

### 環境要求

- Python 3.11+
- OpenCV
- gRPC

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 本地運行

```bash
# 設置環境變量
export CONFIG_PATH=./config/config.yaml

# 啟動服務
python cmd/server.py
```

### Docker部署

```bash
# 構建鏡像
docker build -t suoke/look-service:latest .

# 運行容器
docker run -p 50053:50053 suoke/look-service:latest
```

### Kubernetes部署

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
```

## API說明

服務透過gRPC協議提供以下主要API：

- `AnalyzeFace` - 分析面色
- `AnalyzeBody` - 分析形體
- `AnalyzeTongue` - 分析舌象
- `GetAnalysisHistory` - 獲取用戶分析歷史
- `CompareAnalysis` - 比較分析結果
- `HealthCheck` - 健康檢查

詳細API文檔見 [API文檔](../../../docs/api/look_service_api.md)

## 測試

### 單元測試

```bash
# 運行所有單元測試
pytest test/unit

# 運行特定測試
pytest test/unit/test_face_analyzer.py
```

### 集成測試

```bash
# 運行集成測試
pytest test/integration
```

### 性能測試

```bash
# 運行性能測試
python test/performance/test_service_performance.py
```

## 開發指南

### 代碼規範

- 使用Black進行代碼格式化
- 使用Pylint進行代碼靜態分析
- 遵循PEP 8編碼規範

### 提交前檢查

```bash
# 運行格式化
black .

# 運行靜態分析
pylint **/*.py

# 運行單元測試
pytest
```

## 監控與可觀測性

- **Prometheus指標**：服務暴露在`/metrics`端點
- **日誌**：結構化日誌輸出到`logs/look_service.log`
- **分佈式追蹤**：支持OpenTelemetry與Jaeger集成

### 主要監控指標

| 指標名稱 | 指標類型 | 描述 |
|---------|---------|------|
| look_service_requests_total | 計數器 | 按方法和狀態分類的請求總數 |
| look_service_request_latency_seconds | 直方圖 | 請求處理延遲（秒） |
| look_service_active_requests | 量表 | 當前活躍請求數 |
| look_service_image_size_bytes | 摘要 | 按分析類型的圖像大小（字節） |
| look_service_errors_total | 計數器 | 按錯誤類型的錯誤計數 |
| look_service_db_operation_seconds | 直方圖 | 數據庫操作耗時（秒） |
| look_service_model_execution_seconds | 直方圖 | 模型執行耗時（秒） |

## 故障排除

常見問題和解決方案：

1. **服務啟動失敗**：檢查配置文件路徑和內容是否正確
2. **分析失敗**：檢查圖像格式和大小是否支持
3. **集成失敗**：檢查xiaoai-service是否可達
4. **性能問題**：檢查資源配置和並發設置

## 與其他服務集成

### 與小艾服務集成

望診服務通過gRPC協議與小艾服務(xiaoai-service)集成。每次望診分析完成後，結果會自動發送給小艾服務，用於進一步的四診合參分析。

配置示例：

```yaml
integration:
  xiaoai_service:
    host: "xiaoai-service.suoke-diagnostic.svc.cluster.local"
    port: 50050
    timeout_ms: 5000
    max_retries: 3
    retry_interval_ms: 1000
    circuit_breaker:
      failure_threshold: 5
      reset_timeout_ms: 30000
```

### 與API網關集成

望診服務可以通過API網關暴露給外部客戶端，例如移動應用和Web應用。API網關負責身份驗證、授權、請求路由和負載均衡。

## 貢獻指南

1. Fork該倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 提交Pull Request

## 版本歷史

- v1.0.0 - 初始版本
- v1.1.0 - 添加形體分析功能
- v1.2.0 - 改進面色分析算法
- v1.3.0 - 與xiaoai-service集成

## 許可證

版權所有 © 2024 索克生活科技 