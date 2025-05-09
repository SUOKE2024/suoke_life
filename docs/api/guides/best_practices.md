# API 最佳实践指南

## 概述

本文档提供了索克生活APP API的最佳实践指南，旨在帮助开发者更高效、安全地使用API。遵循这些最佳实践可以提升应用性能、降低错误率并提供更好的用户体验。

## API调用基础规范

### 1. 认证与授权

- **始终使用HTTPS**: 所有API请求必须通过HTTPS发送，确保传输安全。
- **妥善保管令牌**: 客户端应安全存储访问令牌，避免泄露。
- **实现令牌刷新机制**: 在访问令牌过期前自动刷新，避免用户会话中断。
- **定期轮换刷新令牌**: 长期未使用的刷新令牌应主动更新，提高安全性。

```dart
// 推荐的令牌管理示例
class TokenManager {
  Future<String> getAccessToken() async {
    final token = await _getStoredToken();
    if (_isTokenExpired(token)) {
      return await _refreshToken();
    }
    return token;
  }
  
  Future<String> _refreshToken() async {
    // 实现刷新令牌逻辑
  }
}
```

### 2. 请求与响应处理

- **合理使用分页**: 请求大量数据时使用分页，避免一次性加载过多数据。
- **指定响应字段**: 使用字段筛选参数(`fields`)请求所需字段，减少传输数据量。
- **实现请求重试**: 对于网络错误实现智能重试机制，但避免对服务端错误盲目重试。
- **缓存响应数据**: 适当缓存不经常变化的数据，减少请求次数。

```dart
// 推荐的分页请求示例
Future<List<HealthRecord>> fetchHealthRecords({
  int page = 1,
  int pageSize = 20,
  String sortBy = 'createdAt',
  String sortOrder = 'desc'
}) async {
  final response = await httpClient.get(
    '/api/v1/health-records',
    queryParameters: {
      'page': page,
      'pageSize': pageSize,
      'sortBy': sortBy,
      'sortOrder': sortOrder,
      'fields': 'id,recordType,value,unit,timestamp'
    }
  );
  
  // 处理响应数据
}
```

### 3. 错误处理

- **全面处理错误**: 针对不同HTTP状态码和错误代码实现特定处理逻辑。
- **提供用户友好提示**: 将技术错误转化为用户可理解的信息。
- **记录关键错误**: 将关键错误记录到日志系统，便于调试和改进。
- **优雅降级**: 在API不可用时提供离线功能或备用方案。

```dart
// 推荐的错误处理示例
Future<void> handleApiRequest(Future<Response> Function() apiCall) async {
  try {
    final response = await apiCall();
    return _processResponse(response);
  } on DioException catch (e) {
    if (e.type == DioExceptionType.connectionTimeout) {
      throw UserFriendlyException('网络连接超时，请检查网络设置');
    } else if (e.response?.statusCode == 401) {
      throw AuthException('登录已过期，请重新登录');
    } else if (e.response?.statusCode == 503) {
      throw ServiceUnavailableException('服务暂时不可用，请稍后再试');
    }
    
    // 记录错误
    _logError(e);
    throw UnknownException('操作失败，请稍后再试');
  }
}
```

## 性能优化

### 1. 批量操作

- **合并多个请求**: 使用批量API接口一次性处理多条记录，减少网络往返。
- **减少轮询**: 避免频繁轮询获取状态更新，优先使用WebSocket或服务器推送。

```dart
// 批量操作示例
Future<void> syncHealthData(List<HealthDataPoint> dataPoints) async {
  // 不推荐: 逐条同步
  // for (var point in dataPoints) {
  //   await uploadHealthData(point);
  // }
  
  // 推荐: 批量同步
  await httpClient.post(
    '/api/v1/health-data/batch',
    data: {'items': dataPoints.map((p) => p.toJson()).toList()}
  );
}
```

### 2. 数据压缩与优化

- **启用压缩**: 设置HTTP请求头接受压缩响应，减少传输数据量。
- **限制请求频率**: 实现节流(throttling)和防抖(debouncing)，避免过于频繁的API调用。
- **优化上传文件**: 在客户端压缩图片后再上传，减少传输时间。

```dart
// HTTP客户端配置示例
final dio = Dio(BaseOptions(
  baseUrl: 'https://api.suoke.life',
  // 启用gzip解压
  responseDecoder: (responseBytes, options, responseBody) {
    if (options.headers['content-encoding']?.contains('gzip') == true) {
      return utf8.decode(GZipCodec().decode(responseBytes));
    }
    return utf8.decode(responseBytes);
  },
  headers: {
    'Accept-Encoding': 'gzip, deflate'
  }
));
```

### 3. 缓存策略

- **实现多级缓存**: 组合内存缓存和持久化缓存，优化数据访问效率。
- **使用Cache-Control**: 遵循响应中的缓存指令，合理缓存资源。
- **实现条件请求**: 使用ETags或Last-Modified头进行条件请求，避免重复获取未变更数据。

```dart
// 推荐的缓存管理示例
class ApiCache {
  final Map<String, CacheEntry> _memoryCache = {};
  final CacheDatabase _diskCache;
  
  Future<T> getOrFetch<T>(
    String key,
    Future<T> Function() fetcher,
    {Duration maxAge = const Duration(minutes: 15)}
  ) async {
    // 优先从内存缓存获取
    if (_memoryCache.containsKey(key)) {
      final entry = _memoryCache[key]!;
      if (!entry.isExpired()) {
        return entry.data as T;
      }
    }
    
    // 其次从持久化缓存获取
    final diskEntry = await _diskCache.get(key);
    if (diskEntry != null && !diskEntry.isExpired()) {
      _memoryCache[key] = diskEntry;
      return diskEntry.data as T;
    }
    
    // 最后从网络获取
    final data = await fetcher();
    final entry = CacheEntry(data, DateTime.now().add(maxAge));
    _memoryCache[key] = entry;
    await _diskCache.set(key, entry);
    return data;
  }
}
```

## 特定场景最佳实践

### 1. 健康数据同步

- **增量同步**: 优先使用增量同步而非全量同步，减少数据传输量。
- **后台同步**: 实现应用后台自动同步机制，保持数据最新。
- **冲突解决**: 设计明确的数据冲突解决策略，确保数据一致性。
- **分批同步**: 大量数据分批次同步，避免单次请求过大。

```dart
// 增量同步示例
Future<void> syncHealthData() async {
  final lastSyncTime = await getLastSyncTime();
  
  final newData = await httpClient.get(
    '/api/v1/health-data/sync',
    queryParameters: {
      'since': lastSyncTime.toIso8601String()
    }
  );
  
  await saveNewData(newData);
  await updateLastSyncTime(DateTime.now());
}
```

### 2. 图像上传与处理

- **渐进式上传**: 对于大型图像，先上传低分辨率预览，再上传完整图像。
- **本地预处理**: 上传前在客户端进行图像裁剪、压缩和格式转换。
- **智能重试**: 图像上传失败时实现断点续传或分块上传重试。
- **后台上传**: 实现后台上传功能，允许用户继续使用应用。

```dart
// 图像预处理与上传示例
Future<String> uploadTongueImage(File imageFile) async {
  // 压缩图像
  final compressedFile = await compressImage(
    imageFile,
    maxWidth: 1024,
    maxHeight: 1024,
    quality: 85
  );
  
  // 创建上传表单
  final formData = FormData.fromMap({
    'image': await MultipartFile.fromFile(
      compressedFile.path,
      contentType: MediaType('image', 'jpeg')
    ),
    'type': 'TONGUE',
    'metadata': jsonEncode({
      'deviceModel': await getDeviceModel(),
      'timestamp': DateTime.now().toIso8601String()
    })
  });
  
  // 执行上传
  final response = await httpClient.post(
    '/api/v1/diagnoses/inspection/images',
    data: formData,
    onSendProgress: (sent, total) {
      // 更新上传进度
      final progress = sent / total;
      updateUploadProgress(progress);
    }
  );
  
  return response.data['imageUrl'];
}
```

### 3. 智能体交互

- **会话管理**: 维护智能体会话状态，确保对话连贯性。
- **流式响应处理**: 对于长响应内容，使用流式API获取实时反馈。
- **本地缓存上下文**: 缓存关键上下文信息，减少冗余请求。
- **优雅降级**: 网络不稳定时优先使用本地智能体能力，保障核心体验。

```dart
// 智能体流式交互示例
Stream<AgentResponse> chatWithAgent(String message) async* {
  final sessionId = await getOrCreateSessionId();
  
  final response = await httpClient.post(
    '/api/v1/agents/ai/chat',
    data: {
      'message': message,
      'sessionId': sessionId,
      'stream': true
    },
    options: Options(
      responseType: ResponseType.stream
    )
  );
  
  final stream = response.data.stream as Stream<List<int>>;
  await for (var chunk in stream.transform(utf8.decoder)) {
    if (chunk.trim().isNotEmpty) {
      yield AgentResponse.fromJson(jsonDecode(chunk));
    }
  }
}
```

## 安全最佳实践

### 1. 敏感数据处理

- **最小化数据收集**: 只收集必要的个人信息，遵循数据最小化原则。
- **敏感数据加密**: 在本地存储敏感数据前进行加密。
- **传输保护**: 敏感信息传输时应使用额外加密措施。
- **隐私优先设计**: 实现用户可控的数据收集和使用机制。

```dart
// 敏感数据存储示例
class SecureStorage {
  final FlutterSecureStorage _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock,
    ),
  );
  
  Future<void> saveHealthData(String key, String value) async {
    await _storage.write(key: 'health_$key', value: value);
  }
  
  Future<String?> getHealthData(String key) async {
    return await _storage.read(key: 'health_$key');
  }
}
```

### 2. 用户身份保护

- **验证输入**: 所有用户输入必须经过验证，防止注入攻击。
- **防御CSRF攻击**: 实现CSRF令牌验证机制。
- **限制请求频率**: 实现登录尝试限制，防止暴力破解。
- **安全注销**: 确保注销时完全清除本地令牌和状态。

```dart
// 安全注销示例
Future<void> secureLogout() async {
  try {
    // 通知服务器吊销令牌
    await httpClient.post('/api/v1/auth/logout');
  } catch (e) {
    // 即使服务器请求失败也继续清理本地状态
    _logError(e);
  } finally {
    // 清除本地令牌和会话数据
    await _tokenStorage.clearAll();
    await _sessionManager.clearSession();
    await _secureStorage.deleteAll();
    
    // 清除内存中的敏感数据
    _currentUser = null;
    _accessToken = null;
    _refreshToken = null;
  }
}
```

### 3. 设备安全

- **设备绑定**: 实现设备指纹与账户绑定，检测异常登录。
- **生物认证**: 集成生物识别认证保护敏感操作。
- **应用锁定**: 提供应用级密码锁定选项。
- **远程擦除**: 支持远程撤销访问权限和数据擦除。

```dart
// 生物认证示例
Future<bool> authenticateForHealthData() async {
  final localAuth = LocalAuthentication();
  final canAuthenticate = await localAuth.canCheckBiometrics;
  
  if (!canAuthenticate) {
    return false;
  }
  
  return await localAuth.authenticate(
    localizedReason: '需要验证您的身份以访问健康数据',
    options: const AuthenticationOptions(
      biometricOnly: true,
      stickyAuth: true,
    ),
  );
}
```

## 客户端开发最佳实践

### 1. 网络状态管理

- **连接监控**: 实时监控网络状态变化，适当调整API调用策略。
- **离线模式**: 在无网络情况下提供基本功能，并队列化待同步操作。
- **重连逻辑**: 网络恢复时自动重新同步数据。
- **带宽感知**: 根据网络类型(WiFi/移动网络)调整数据同步策略。

```dart
// 网络状态监控示例
class NetworkManager {
  final connectivity = Connectivity();
  ConnectivityResult _connectionStatus = ConnectivityResult.none;
  final _controller = StreamController<ConnectivityResult>.broadcast();
  
  Stream<ConnectivityResult> get connectionStream => _controller.stream;
  
  Future<void> initialize() async {
    _connectionStatus = await connectivity.checkConnectivity();
    
    connectivity.onConnectivityChanged.listen((result) {
      if (_connectionStatus != result) {
        _connectionStatus = result;
        _controller.add(result);
        
        if (result != ConnectivityResult.none) {
          // 网络恢复，执行同步
          _synchronizeData();
        }
      }
    });
  }
  
  bool get isConnected => _connectionStatus != ConnectivityResult.none;
  bool get isOnWifi => _connectionStatus == ConnectivityResult.wifi;
  
  Future<void> _synchronizeData() async {
    // 网络恢复后的同步逻辑
  }
}
```

### 2. 数据持久化

- **分层存储**: 根据数据敏感度和使用频率选择不同存储方式。
- **优化查询**: 设计高效的本地数据库查询和索引。
- **数据迁移**: 实现版本化的数据库迁移策略。
- **存储限制**: 监控存储空间使用，实现数据清理机制。

```dart
// SQLite数据库管理示例
class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  static Database? _database;
  
  factory DatabaseHelper() => _instance;
  
  DatabaseHelper._internal();
  
  Future<Database> get database async {
    if (_database != null) return _database!;
    
    _database = await initDatabase();
    return _database!;
  }
  
  Future<Database> initDatabase() async {
    final path = await getDatabasePath();
    return await openDatabase(
      path,
      version: 1,
      onCreate: _createDatabase,
      onUpgrade: _upgradeDatabase
    );
  }
  
  Future<void> _createDatabase(Database db, int version) async {
    await db.execute('''
      CREATE TABLE health_records (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        record_type TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        synced INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
      )
    ''');
    
    // 创建索引
    await db.execute(
      'CREATE INDEX idx_health_records_user_timestamp ON health_records(user_id, timestamp)'
    );
  }
  
  Future<void> _upgradeDatabase(Database db, int oldVersion, int newVersion) async {
    // 数据库迁移逻辑
  }
}
```

### 3. 用户体验优化

- **透明重试**: 在网络错误时自动重试，对用户透明。
- **进度反馈**: 长时间操作提供明确的进度指示。
- **预加载数据**: 提前加载用户可能需要的数据，减少等待时间。
- **智能预测**: 基于用户行为模式预测下一步操作，预先准备数据。

```dart
// 预加载数据示例
class DataPreloader {
  Future<void> preloadUserDashboard() async {
    // 并行预加载多种数据
    await Future.wait([
      _profileManager.loadUserProfile(),
      _healthManager.loadRecentHealthData(),
      _contentManager.loadRecommendedContent(),
      _serviceManager.loadPopularServices()
    ]);
  }
  
  Future<void> preloadHealthAnalysis() async {
    // 根据用户最近的操作模式，预测用户可能需要的分析
    final recentAnalysisTypes = await _userBehaviorTracker.getRecentAnalysisTypes();
    for (final type in recentAnalysisTypes) {
      unawaited(_healthAnalyzer.preloadAnalysisModel(type));
    }
  }
}
```

## 测试与调试

### 1. API测试

- **单元测试**: 为API客户端封装编写单元测试，验证请求构建和响应解析。
- **模拟测试**: 使用模拟服务器测试各种响应场景，包括错误处理。
- **集成测试**: 编写端到端测试验证完整API流程。
- **性能基准**: 建立API性能基准，监控性能退化。

```dart
// API客户端测试示例
void main() {
  group('UserApiClient tests', () {
    late MockHttpClient mockClient;
    late UserApiClient apiClient;
    
    setUp(() {
      mockClient = MockHttpClient();
      apiClient = UserApiClient(client: mockClient);
    });
    
    test('getUserProfile should correctly parse response', () async {
      // 安排模拟响应
      when(mockClient.get('/api/v1/users/me')).thenAnswer((_) async => 
        Response(
          data: {'id': 'user123', 'name': '张三', 'email': 'zhang@example.com'},
          statusCode: 200
        )
      );
      
      // 执行测试
      final profile = await apiClient.getUserProfile();
      
      // 验证结果
      expect(profile.id, equals('user123'));
      expect(profile.name, equals('张三'));
      expect(profile.email, equals('zhang@example.com'));
    });
    
    test('getUserProfile should handle unauthorized error', () async {
      // 安排模拟响应
      when(mockClient.get('/api/v1/users/me')).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: '/api/v1/users/me'),
          response: Response(
            data: {'code': 'UNAUTHORIZED', 'message': '未授权访问'},
            statusCode: 401
          )
        )
      );
      
      // 执行测试并验证异常
      expect(() => apiClient.getUserProfile(), throwsA(isA<AuthException>()));
    });
  });
}
```

### 2. 日志与监控

- **结构化日志**: 使用结构化日志格式，便于分析和过滤。
- **敏感信息过滤**: 确保日志中不包含敏感信息。
- **性能监控**: 记录API调用性能指标，发现性能瓶颈。
- **错误聚合**: 实现错误聚合和分析，识别常见问题。

```dart
// 日志工具示例
class ApiLogger {
  final Logger _logger = Logger();
  
  void logRequest(RequestOptions options) {
    _logger.info('API Request', {
      'method': options.method,
      'path': options.path,
      'timestamp': DateTime.now().toIso8601String(),
      'headers': _sanitizeHeaders(options.headers),
      // 不记录请求体，可能包含敏感信息
    });
  }
  
  void logResponse(Response response) {
    _logger.info('API Response', {
      'statusCode': response.statusCode,
      'path': response.requestOptions.path,
      'duration': response.requestOptions.extra['duration'],
      'timestamp': DateTime.now().toIso8601String(),
      // 不记录响应体，可能包含敏感信息
    });
  }
  
  void logError(DioException error) {
    _logger.error('API Error', {
      'statusCode': error.response?.statusCode,
      'path': error.requestOptions.path,
      'errorType': error.type.toString(),
      'message': error.message,
      'timestamp': DateTime.now().toIso8601String()
    });
  }
  
  Map<String, dynamic> _sanitizeHeaders(Map<String, dynamic> headers) {
    final result = Map<String, dynamic>.from(headers);
    // 移除敏感头信息
    result.remove('Authorization');
    result.remove('Cookie');
    return result;
  }
}
```

## API版本与兼容性

### 1. 版本管理

- **使用API版本前缀**: 在URL中包含API版本，如`/api/v1/users`。
- **平滑升级**: 同时支持多个API版本，允许客户端逐步迁移。
- **版本兼容性**: 保持向后兼容性，避免破坏性变更。
- **弃用通知**: 提前通知API版本弃用计划，给予充分迁移时间。

### 2. 特性检测

- **能力发现**: 实现API能力发现机制，客户端可检测服务器支持的功能。
- **优雅降级**: 当服务器不支持新功能时，客户端优雅降级。
- **动态配置**: 通过配置端点获取当前环境参数和限制。

```dart
// API能力检测示例
class ApiCapabilityChecker {
  Map<String, bool> _capabilities = {};
  
  Future<void> initialize() async {
    try {
      final response = await httpClient.get('/api/v1/capabilities');
      _capabilities = Map<String, bool>.from(response.data);
    } catch (e) {
      _logError(e);
      // 默认假设仅支持基本功能
      _capabilities = {'basic': true};
    }
  }
  
  bool hasCapability(String feature) {
    return _capabilities[feature] ?? false;
  }
  
  Future<T> withCapability<T>({
    required String feature,
    required Future<T> Function() whenSupported,
    required Future<T> Function() whenUnsupported
  }) async {
    if (hasCapability(feature)) {
      return await whenSupported();
    } else {
      return await whenUnsupported();
    }
  }
}
```

## 总结

遵循本文档中的最佳实践可以帮助开发者构建高效、可靠且安全的索克生活APP集成。这些实践旨在提升应用性能、增强用户体验、保护用户数据安全，同时也有助于减少开发和维护成本。

随着API的演进，我们将持续更新本文档，确保开发者始终获得最新的指导和建议。

## 附录

### 常见错误代码及处理建议

| 错误代码 | 描述 | 处理建议 |
|---------|------|---------|
| UNAUTHORIZED | 未授权或token无效 | 引导用户重新登录 |
| TOKEN_EXPIRED | 令牌已过期 | 尝试刷新令牌，失败则重新登录 |
| RESOURCE_NOT_FOUND | 请求的资源不存在 | 检查ID是否正确，必要时刷新数据 |
| VALIDATION_ERROR | 请求参数验证失败 | 根据错误详情调整输入 |
| RATE_LIMITED | 请求频率超限 | 实现指数退避重试策略 |
| INSUFFICIENT_PERMISSIONS | 权限不足 | 通知用户权限限制 |
| SERVICE_UNAVAILABLE | 服务暂时不可用 | 延迟重试，并提供离线功能 |

### 有用的开发工具

- **Postman/Insomnia**: API测试工具
- **Charles/Fiddler**: HTTP分析代理
- **Flipper**: 移动应用调试工具
- **Firebase Performance Monitoring**: 性能监控
- **Sentry/Crashlytics**: 错误跟踪
- **OpenAPI Generator**: 从规范生成API客户端

### 相关文档

- [API参考文档](/docs/api/api_documentation.md)
- [认证指南](/docs/api/endpoints/auth.md)
- [数据模型参考](/docs/api/models/common.md)
- [错误处理指南](/docs/api/guides/error_handling.md)
- [性能优化指南](/docs/api/guides/performance.md)

---

> 文档最后更新：2024年7月15日 