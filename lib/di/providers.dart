// TODO: 这些包引用在实际部署时需要使用真实包替换
// import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:dio/dio.dart' hide ResponseType;
// import 'package:flutter_secure_storage/flutter_secure_storage.dart';
// import 'package:sqflite/sqflite.dart' show Database;

// 引入系统包和自定义包
import 'dart:async';
import 'dart:convert';
import 'dart:math';

import '../core/network/api_client.dart';
import '../core/network/interceptors/auth_interceptor.dart';
import '../core/network/interceptors/error_interceptor.dart';
import '../core/network/interceptors/logging_interceptor.dart';
import '../core/storage/database_helper.dart';
import '../core/storage/database_service.dart';
import '../core/storage/secure_storage.dart';
import '../core/utils/logger.dart';

import '../ai_agents/core/agent_microkernel.dart';
import '../ai_agents/core/autonomous_learning_system.dart';
import '../ai_agents/core/security_privacy_framework.dart';
import '../ai_agents/integration/service_integration.dart';
import '../ai_agents/integration/medical_service_api.dart';
import '../ai_agents/factory/agent_factory.dart';
import '../ai_agents/registry/agent_registry.dart';
import '../ai_agents/user_interaction/multimodal_interaction_engine.dart';
import '../ai_agents/user_interaction/personalization_system.dart';
import '../ai_agents/rag/rag_service.dart';
import '../ai_agents/models/ai_agent.dart';
import '../ai_agents/models/embedding.dart';

// Expert agents
import '../ai_agents/expert/health_management_agent.dart';
import '../ai_agents/expert/exercise_planning_agent.dart';
import '../ai_agents/expert/medical_diagnosis_agent.dart';
import '../ai_agents/expert/mental_health_agent.dart';
import '../ai_agents/expert/nutrition_balance_agent.dart';
import '../ai_agents/expert/sleep_optimization_agent.dart';
import '../ai_agents/expert/knowledge_graph_agent.dart';

// Supply chain agents
import '../ai_agents/supply_chain/agriculture_agent.dart';
// 避免名称冲突，使用别名
import '../ai_agents/supply_chain/medicinal_food_agent.dart' as supply_chain;

import '../domain/repositories/knowledge_graph_repository.dart';
import '../domain/repositories/knowledge_repository.dart';
import '../domain/repositories/vector_store_repository.dart';

/// Provider接口模拟实现
class Provider<T> {
  final T Function(ProviderRef<T>) create;

  Provider(this.create);

  T read(ProviderRef<T> ref) => create(ref);
}

/// FutureProvider接口模拟实现
class FutureProvider<T> {
  final Future<T> Function(ProviderRef<T>) create;

  FutureProvider(this.create);

  Future<T> read(ProviderRef<T> ref) => create(ref);
}

/// ProviderRef接口模拟实现
class ProviderRef<T> {
  R watch<R>(Provider<R> provider) {
    return provider.read(this as ProviderRef<R>);
  }

  R read<R>(Provider<R> provider) {
    return provider.read(this as ProviderRef<R>);
  }

  Future<R> watchAsync<R>(FutureProvider<R> provider) {
    return provider.read(this as ProviderRef<R>);
  }
}

/// AsyncValue接口模拟实现
class AsyncValue<T> {
  final T? _value;
  final Object? _error;

  AsyncValue.data(this._value) : _error = null;
  AsyncValue.error(this._error, StackTrace stackTrace) : _value = null;

  T? get valueOrNull => _value;
  bool get hasError => _error != null;
  Object? get error => _error;
}

/// 数据库接口模拟
class Database {
  Future<void> execute(String sql) async {}
  Future<List<Map<String, dynamic>>> query(
    String table, {
    String? where,
    List<Object?>? whereArgs,
    String? orderBy,
    int? limit,
    List<String>? columns,
  }) async => [];
  Future<int> insert(
    String table,
    Map<String, dynamic> values, {
    int? conflictAlgorithm,
  }) async => 0;
  Future<int> update(
    String table,
    Map<String, dynamic> values, {
    String? where,
    List<Object?>? whereArgs,
  }) async => 0;
  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async => 0;
}

/// Dio HTTP客户端模拟
class Dio {
  final List<Interceptor> interceptors = [];

  Future<Map<String, dynamic>> get(String path) async => {};
  Future<Map<String, dynamic>> post(String path, {dynamic data}) async => {};
  Future<Map<String, dynamic>> put(String path, {dynamic data}) async => {};
  Future<Map<String, dynamic>> delete(String path) async => {};
}

/// 拦截器接口
abstract class Interceptor {}

/// 数据库助手定义
class DatabaseHelper {
  Database? database;

  Future<void> initialize() async {
    // 在实际实现中，这里会初始化SQLite数据库
    database = Database();
  }
}

/// 数据库服务扩展
extension DatabaseServiceExtension on DatabaseService {
  Future<void> execute(String sql) async {
    // 在实际实现中，这会调用底层数据库的execute方法
    if (this.database != null) {
      await this.database!.execute(sql);
    }
  }
}

/// 安全存储模拟
class FlutterSecureStorage {
  const FlutterSecureStorage();

  Future<String?> read({required String key}) async => null;
  Future<void> write({required String key, required String? value}) async {}
  Future<void> delete({required String key}) async {}
}

/// 项目当前注册的所有Provider
/// 此文件替代了GetIt实现的service_locator.dart

//===== 核心服务 =====//

/// 数据库Helper Provider
final databaseHelperProvider = Provider<DatabaseHelper>((ref) {
  final databaseHelper = DatabaseHelper();
  // 注意：这里需要在使用前确保数据库已初始化
  return databaseHelper;
});

/// 数据库实例Provider (异步)
final databaseInitProvider = FutureProvider<Database?>((ref) async {
  final databaseHelper = ref.watch(databaseHelperProvider);
  await databaseHelper.initialize();
  return databaseHelper.database;
});

/// 数据库实例Provider (同步，用于已初始化情况)
final databaseProvider = Provider<Database>((ref) {
  final database =
      ref
          .watch(databaseInitProvider as Provider<AsyncValue<Database?>>)
          .valueOrNull;
  if (database == null) {
    throw Exception('数据库尚未初始化');
  }
  return database;
});

/// 数据库服务Provider
final databaseServiceProvider = Provider<DatabaseService>((ref) {
  final database = ref.watch(databaseProvider);
  return DatabaseService(database);
});

/// 安全存储Provider
final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage();
});

/// 安全存储服务Provider
final secureStorageServiceProvider = Provider<SecureStorage>((ref) {
  final secureStorage = ref.watch(secureStorageProvider);
  return SecureStorage(secureStorage);
});

//===== 网络服务 =====//

/// 认证拦截器Provider
final authInterceptorProvider = Provider<AuthInterceptor>((ref) {
  final secureStorage = ref.watch(secureStorageServiceProvider);
  return AuthInterceptor(secureStorage);
});

/// 错误拦截器Provider
final errorInterceptorProvider = Provider<ErrorInterceptor>((ref) {
  return ErrorInterceptor();
});

/// 日志拦截器Provider
final loggingInterceptorProvider = Provider<LoggingInterceptor>((ref) {
  return LoggingInterceptor(
    logRequestBody: true,
    logResponseBody: true,
    logHeaders: true,
  );
});

/// Dio HTTP客户端Provider
final dioProvider = Provider<Dio>((ref) {
  final dio = Dio();

  // 添加拦截器
  dio.interceptors.addAll([
    ref.read(authInterceptorProvider as Provider<Interceptor>),
    ref.read(errorInterceptorProvider as Provider<Interceptor>),
    ref.read(loggingInterceptorProvider as Provider<Interceptor>),
  ]);

  return dio;
});

/// API客户端Provider
final apiClientProvider = Provider<ApiClient>((ref) {
  final dio = ref.watch(dioProvider);
  return ApiClient(dio);
});

//===== 领域存储库 =====//

/// 知识图谱存储库Provider
final knowledgeGraphRepositoryProvider = Provider<KnowledgeGraphRepository>((
  ref,
) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  // 这里使用了动态类型转换
  return LocalKnowledgeGraphRepository(databaseHelper as dynamic);
});

/// 知识存储库Provider
final knowledgeRepositoryProvider = Provider<KnowledgeRepository>((ref) {
  final databaseService = ref.watch(databaseServiceProvider);
  // 返回具体实现类，根据项目实际情况调整
  return LocalKnowledgeRepository(databaseService);
});

/// 向量存储库Provider
final vectorStoreRepositoryProvider = Provider<VectorStoreRepository>((ref) {
  final databaseService = ref.watch(databaseServiceProvider);
  // 返回具体实现类，根据项目实际情况调整
  return LocalVectorStoreRepository(databaseService);
});

//===== AI代理核心服务 =====//

/// 自主学习系统Provider
final autonomousLearningSystemProvider = Provider<AutonomousLearningSystem>((
  ref,
) {
  // 创建一个新的实例而不是使用单例
  return DefaultAutonomousLearningSystem();
});

/// 安全与隐私框架Provider
final securityPrivacyFrameworkProvider = Provider<SecurityPrivacyFramework>((
  ref,
) {
  return DefaultSecurityPrivacyFramework();
});

/// 服务集成注册表Provider
final serviceIntegrationRegistryProvider = Provider<ServiceIntegrationRegistry>(
  (ref) {
    return DefaultServiceIntegrationRegistry();
  },
);

/// 医疗服务API Provider
final medicalServiceApiProvider = Provider<MedicalServiceAPI>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return DefaultMedicalServiceAPI(apiClient);
});

/// 个性化系统Provider
final personalizationSystemProvider = Provider<PersonalizationSystem>((ref) {
  return DefaultPersonalizationSystem();
});

/// 代理微内核Provider(初始)
/// 此Provider用于打破循环依赖
final initialMicrokernelProvider = Provider<AgentMicrokernel>((ref) {
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final registry = ref.watch(initialRegistryProvider);
  return DefaultAgentMicrokernel(registry, learningSystem);
});

/// 代理注册表Provider(初始)
/// 此Provider用于打破循环依赖
final initialRegistryProvider = Provider<AgentRegistry>((ref) {
  // 使用具体实现类而非抽象类
  final emptyLearningSystem = DefaultAutonomousLearningSystem();

  // 创建一个临时的初始化微内核和工厂
  final tempMicrokernel = DefaultAgentMicrokernel(null, emptyLearningSystem);
  final tempFactory = DefaultAgentFactory(
    tempMicrokernel,
    emptyLearningSystem,
    DefaultSecurityPrivacyFramework(),
    DefaultServiceIntegrationRegistry(),
  );

  // 使用临时对象创建registry
  final emptyRegistry = DefaultAgentRegistry(tempMicrokernel, tempFactory);

  // 使用初始化的实例
  return emptyRegistry;
});

/// 代理工厂Provider
final agentFactoryProvider = Provider<AgentFactory>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final securityFramework = ref.watch(securityPrivacyFrameworkProvider);
  final serviceRegistry = ref.watch(serviceIntegrationRegistryProvider);

  return DefaultAgentFactory(
    microkernel,
    learningSystem,
    securityFramework,
    serviceRegistry,
  );
});

/// 最终代理注册表Provider
/// 依赖于agentFactoryProvider
final agentRegistryProvider = Provider<AgentRegistry>((ref) {
  final initialRegistry = ref.watch(initialRegistryProvider);
  final factory = ref.watch(agentFactoryProvider);

  // 更新初始注册表
  if (initialRegistry is DefaultAgentRegistry) {
    initialRegistry.setFactory(factory);
  }

  return initialRegistry;
});

/// RAG服务Provider
final ragServiceProvider = Provider<RAGService>((ref) {
  final vectorStoreRepository = ref.watch(vectorStoreRepositoryProvider);
  final knowledgeRepository = ref.watch(knowledgeRepositoryProvider);

  return DefaultRAGService(
    vectorStoreRepository: vectorStoreRepository,
    knowledgeRepository: knowledgeRepository,
  );
});

/// 多模态交互引擎Provider
final multimodalInteractionEngineProvider =
    Provider<MultimodalInteractionEngine>((ref) {
      final registry = ref.watch(agentRegistryProvider);
      return MultimodalInteractionEngine(registry);
    });

//===== 专家代理 Provider =====//

/// 健康管理代理Provider
final healthManagementAgentProvider = Provider<HealthManagementAgent>((ref) {
  final agent = AIAgent.laoke;
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);
  return BaseHealthManagementAgent(
    agent,
    learningSystem,
    ragService,
    microkernel,
  );
});

/// 运动规划代理Provider
final exercisePlanningAgentProvider = Provider<ExercisePlanningAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultExercisePlanningAgent(microkernel, learningSystem);
});

/// 医学诊断代理Provider
final medicalDiagnosisAgentProvider = Provider<MedicalDiagnosisAgent>((ref) {
  final agent = AIAgent.xiaoai.copyWith(
    modelConfig: {
      ...AIAgent.xiaoai.modelConfig,
      'supports_tcm': true,
      'supports_western': true,
    },
  );
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);

  // 返回中西医结合诊断代理
  return IntegratedMedicalDiagnosisAgent(
    agent,
    learningSystem,
    ragService,
    microkernel,
  );
});

/// 中医诊断代理Provider
final tcmDiagnosisAgentProvider = Provider<TCMMedicalDiagnosisAgent>((ref) {
  final agent = AIAgent.laoke.copyWith(
    modelConfig: {
      ...AIAgent.laoke.modelConfig,
      'supports_tcm': true,
      'supports_western': false,
    },
  );
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  final ragService = ref.watch(ragServiceProvider);

  return TCMMedicalDiagnosisAgent(
    agent,
    learningSystem,
    ragService,
    microkernel,
  );
});

/// 西医诊断代理Provider
final westernMedicalDiagnosisAgentProvider =
    Provider<WesternMedicalDiagnosisAgent>((ref) {
      final agent = AIAgent.xiaoai.copyWith(
        modelConfig: {
          ...AIAgent.xiaoai.modelConfig,
          'supports_tcm': false,
          'supports_western': true,
        },
      );
      final microkernel = ref.watch(initialMicrokernelProvider);
      final learningSystem = ref.watch(autonomousLearningSystemProvider);
      final ragService = ref.watch(ragServiceProvider);

      return WesternMedicalDiagnosisAgent(
        agent,
        learningSystem,
        ragService,
        microkernel,
      );
    });

/// 心理健康代理Provider
final mentalHealthAgentProvider = Provider<MentalHealthAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultMentalHealthAgent(microkernel, learningSystem);
});

/// 营养平衡代理Provider
final nutritionBalanceAgentProvider = Provider<NutritionBalanceAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultNutritionBalanceAgent(microkernel, learningSystem);
});

/// 睡眠优化代理Provider
final sleepOptimizationAgentProvider = Provider<SleepOptimizationAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultSleepOptimizationAgent(microkernel, learningSystem);
});

/// 知识图谱代理Provider
final knowledgeGraphAgentProvider = Provider<KnowledgeGraphAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final repository = ref.watch(knowledgeGraphRepositoryProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultKnowledgeGraphAgent(microkernel, repository);
});

//===== 供应链代理 Provider =====//

/// 农业代理Provider
final agricultureAgentProvider = Provider<AgricultureAgent>((ref) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return DefaultAgricultureAgent(microkernel, learningSystem);
});

/// 药食同源代理Provider
final medicinalFoodAgentProvider = Provider<supply_chain.MedicinalFoodAgent>((
  ref,
) {
  final microkernel = ref.watch(initialMicrokernelProvider);
  final learningSystem = ref.watch(autonomousLearningSystemProvider);
  // 返回具体实现类，根据项目实际情况调整
  return supply_chain.DefaultMedicinalFoodAgent(microkernel, learningSystem);
});

/// 初始化AI代理Provider
final aiAgentInitializerProvider = FutureProvider<void>((ref) async {
  final agentRegistry = ref.watch(agentRegistryProvider);

  // 预先注册常用代理
  await agentRegistry.initialize();
  logger.i('AI代理初始化完成');
  return;
});

//===== 具体实现类 =====//

/// 本地知识库实现
class LocalKnowledgeRepository implements KnowledgeRepository {
  final DatabaseService _databaseService;

  LocalKnowledgeRepository(this._databaseService);

  @override
  Future<Embedding> generateEmbedding(String text) async {
    try {
      // 简化的本地嵌入生成
      final random = Random(text.hashCode);
      final dimension = 384; // 常见嵌入维度

      // 创建与文本哈希相关的伪随机向量
      final vector = List<double>.generate(
        dimension,
        (i) => random.nextDouble() * 2 - 1,
      );

      // 归一化向量
      final double norm = sqrt(vector.fold(0.0, (sum, v) => sum + v * v));
      final normalizedVector = vector.map((v) => v / norm).toList();

      return Embedding(vector: normalizedVector, text: text);
    } catch (e) {
      logger.e('生成嵌入失败: $e');
      throw Exception('生成嵌入失败: $e');
    }
  }

  @override
  Future<void> indexDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();

      final now = DateTime.now().toIso8601String();

      // 存储到本地数据库
      await _databaseService.insert('knowledge_items', {
        'id': documentId,
        'content': content,
        'metadata': jsonEncode(metadata ?? {}),
        'source': metadata?['source'] ?? 'system',
        'category': metadata?['category'] ?? 'general',
        'created_at': now,
        'updated_at': now,
        'sync_status': 'pending', // 标记为待同步
      });

      logger.i('成功索引文档: $documentId');
    } catch (e) {
      logger.e('索引文档失败: $e');
      throw Exception('索引文档失败: $e');
    }
  }

  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();

      final now = DateTime.now().toIso8601String();

      // 更新本地数据库
      await _databaseService.update(
        'knowledge_items',
        {
          'content': content,
          'metadata': jsonEncode(metadata ?? {}),
          'source': metadata?['source'] ?? 'system',
          'category': metadata?['category'] ?? 'general',
          'updated_at': now,
          'sync_status': 'pending', // 标记为待同步
        },
        where: 'id = ?',
        whereArgs: [documentId],
      );

      logger.i('成功更新文档: $documentId');
    } catch (e) {
      logger.e('更新文档失败: $e');
      throw Exception('更新文档失败: $e');
    }
  }

  @override
  Future<void> deleteDocument(String documentId) async {
    try {
      // 标记为已删除，但不实际删除（软删除）
      await _databaseService.update(
        'knowledge_items',
        {
          'deleted_at': DateTime.now().toIso8601String(),
          'sync_status': 'pending_delete', // 标记为待删除同步
        },
        where: 'id = ?',
        whereArgs: [documentId],
      );

      logger.i('成功标记删除文档: $documentId');
    } catch (e) {
      logger.e('删除文档失败: $e');
      throw Exception('删除文档失败: $e');
    }
  }

  @override
  Future<List<Map<String, dynamic>>> query(
    String query, {
    int limit = 5,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 确保知识表存在
      await _ensureKnowledgeTableExists();

      // 构建查询
      String whereClause = 'content LIKE ? AND deleted_at IS NULL';
      List<Object?> whereArgs = ['%$query%'];

      // 应用过滤器
      if (filter != null) {
        if (filter['category'] != null) {
          whereClause += ' AND category = ?';
          whereArgs.add(filter['category']);
        }

        if (filter['source'] != null) {
          whereClause += ' AND source = ?';
          whereArgs.add(filter['source']);
        }
      }

      // 执行查询
      final results = await _databaseService.query(
        'knowledge_items',
        where: whereClause,
        whereArgs: whereArgs,
        orderBy: 'created_at DESC',
        limit: limit,
      );

      // 转换结果格式
      return results.map((item) {
        return {
          'id': item['id'],
          'content': item['content'],
          'metadata': jsonDecode(item['metadata'] ?? '{}'),
          'score': 0.7, // 本地搜索的默认分数
        };
      }).toList();
    } catch (e) {
      logger.e('本地搜索失败: $e');
      return [];
    }
  }

  @override
  Future<List<String>> getRelevantPassages(
    String query, {
    int limit = 3,
    double minScore = 0.7,
  }) async {
    try {
      // 查询知识库
      final results = await this.query(
        query,
        limit: limit * 2, // 获取更多结果，然后筛选
      );

      // 筛选高分结果，仅返回内容
      final relevantPassages =
          results
              .where((result) => (result['score'] as num) >= minScore)
              .map((result) => result['content'] as String)
              .take(limit)
              .toList();

      return relevantPassages;
    } catch (e) {
      logger.e('获取相关段落失败: $e');
      return [];
    }
  }

  @override
  Future<String> addKnowledgeItem({
    required String content,
    required String source,
    required String category,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 生成ID
      final documentId = 'knowledge_${DateTime.now().millisecondsSinceEpoch}';

      // 添加元数据
      final fullMetadata = {
        'source': source,
        'category': category,
        ...?metadata,
      };

      // 索引文档
      await indexDocument(
        documentId: documentId,
        content: content,
        metadata: fullMetadata,
      );

      return documentId;
    } catch (e) {
      logger.e('添加知识条目失败: $e');
      throw Exception('添加知识条目失败: $e');
    }
  }

  /// 确保知识表存在
  Future<void> _ensureKnowledgeTableExists() async {
    try {
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_items (
          id TEXT PRIMARY KEY,
          content TEXT NOT NULL,
          metadata TEXT,
          source TEXT,
          category TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT,
          deleted_at TEXT,
          sync_status TEXT
        )
      ''');

      // 创建索引
      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items (category)',
      );

      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_items (source)',
      );

      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_knowledge_sync ON knowledge_items (sync_status)',
      );
    } catch (e) {
      logger.e('创建知识表失败: $e');
      throw Exception('创建知识表失败: $e');
    }
  }

  /// 获取待同步的数据
  Future<List<Map<String, dynamic>>> getPendingSyncItems() async {
    try {
      return await _databaseService.query(
        'knowledge_items',
        where: 'sync_status = ? AND deleted_at IS NULL',
        whereArgs: ['pending'],
      );
    } catch (e) {
      logger.e('获取待同步项失败: $e');
      return [];
    }
  }

  /// 获取待删除同步的数据
  Future<List<Map<String, dynamic>>> getPendingDeleteItems() async {
    try {
      return await _databaseService.query(
        'knowledge_items',
        where: 'sync_status = ?',
        whereArgs: ['pending_delete'],
      );
    } catch (e) {
      logger.e('获取待删除同步项失败: $e');
      return [];
    }
  }

  /// 标记项目为已同步
  Future<void> markItemSynced(String documentId) async {
    try {
      await _databaseService.update(
        'knowledge_items',
        {'sync_status': 'synced'},
        where: 'id = ?',
        whereArgs: [documentId],
      );
    } catch (e) {
      logger.e('标记项目已同步失败: $e');
    }
  }

  /// 物理删除已同步的删除项
  Future<void> purgeDeletedSyncedItems() async {
    try {
      await _databaseService.delete(
        'knowledge_items',
        where: 'sync_status = ? AND deleted_at IS NOT NULL',
        whereArgs: ['synced'],
      );
    } catch (e) {
      logger.e('清除已删除同步项失败: $e');
    }
  }
}

/// 本地向量存储实现
class LocalVectorStoreRepository implements VectorStoreRepository {
  final DatabaseService _databaseService;

  // 嵌入缓存，避免重复计算
  final Map<String, Embedding> _embeddingCache = {};

  LocalVectorStoreRepository(this._databaseService);

  @override
  Future<String> addDocument({
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();

      final now = DateTime.now().toIso8601String();
      final documentId =
          embedding.documentId ??
          'doc_${DateTime.now().millisecondsSinceEpoch}';

      // 存储文档内容
      await _databaseService.insert('vector_documents', {
        'id': documentId,
        'content': content,
        'collection': collection,
        'metadata': jsonEncode(metadata ?? {}),
        'created_at': now,
        'updated_at': now,
        'sync_status': 'pending', // 标记为待同步
      });

      // 存储嵌入向量
      await _databaseService.insert('vector_embeddings', {
        'document_id': documentId,
        'collection': collection,
        'embedding': _encodeVector(embedding.vector),
        'dimension': embedding.vector.length,
        'created_at': now,
      });

      return documentId;
    } catch (e) {
      logger.e('添加文档到向量存储失败: $e');
      throw Exception('添加文档到向量存储失败: $e');
    }
  }

  @override
  Future<void> updateDocument({
    required String documentId,
    required String content,
    required Embedding embedding,
    required String collection,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();

      final now = DateTime.now().toIso8601String();

      // 更新文档内容
      await _databaseService.update(
        'vector_documents',
        {
          'content': content,
          'collection': collection,
          'metadata': jsonEncode(metadata ?? {}),
          'updated_at': now,
          'sync_status': 'pending', // 标记为待同步
        },
        where: 'id = ?',
        whereArgs: [documentId],
      );

      // 删除旧的嵌入
      await _databaseService.delete(
        'vector_embeddings',
        where: 'document_id = ?',
        whereArgs: [documentId],
      );

      // 添加新的嵌入
      await _databaseService.insert('vector_embeddings', {
        'document_id': documentId,
        'collection': collection,
        'embedding': _encodeVector(embedding.vector),
        'dimension': embedding.vector.length,
        'created_at': now,
      });
    } catch (e) {
      logger.e('更新向量存储中的文档失败: $e');
      throw Exception('更新向量存储中的文档失败: $e');
    }
  }

  @override
  Future<void> deleteDocument({
    required String documentId,
    required String collection,
  }) async {
    try {
      // 标记为已删除
      await _databaseService.update(
        'vector_documents',
        {
          'deleted_at': DateTime.now().toIso8601String(),
          'sync_status': 'pending_delete', // 标记为待删除同步
        },
        where: 'id = ? AND collection = ?',
        whereArgs: [documentId, collection],
      );
    } catch (e) {
      logger.e('删除向量存储中的文档失败: $e');
      throw Exception('删除向量存储中的文档失败: $e');
    }
  }

  @override
  Future<List<SearchResult>> similaritySearch({
    required Embedding embedding,
    required String collection,
    int limit = 5,
    double minScore = 0.0,
    Map<String, dynamic>? filter,
  }) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();

      // 获取集合中的所有嵌入
      final embeddingsResult = await _databaseService.query(
        'vector_embeddings',
        where: 'collection = ?',
        whereArgs: [collection],
      );

      if (embeddingsResult.isEmpty) {
        return [];
      }

      // 计算相似度
      final similarities = <Map<String, dynamic>>[];

      for (final embeddingRow in embeddingsResult) {
        final documentId = embeddingRow['document_id'] as String;
        final embeddingString = embeddingRow['embedding'] as String;

        try {
          // 解析嵌入
          final vector = _decodeVector(embeddingString);
          final docEmbedding = Embedding(
            vector: vector,
            documentId: documentId,
          );

          // 计算余弦相似度
          final similarity = _cosineSimilarity(
            embedding.vector,
            docEmbedding.vector,
          );

          if (similarity >= minScore) {
            similarities.add({'document_id': documentId, 'score': similarity});
          }
        } catch (e) {
          logger.w('解析嵌入失败: $e');
          continue;
        }
      }

      // 按相似度排序
      similarities.sort(
        (a, b) => (b['score'] as double).compareTo(a['score'] as double),
      );

      // 如果没有结果，返回空列表
      if (similarities.isEmpty) {
        return [];
      }

      // 获取文档内容
      final results = <SearchResult>[];

      for (final similarity in similarities.take(limit)) {
        final documentId = similarity['document_id'] as String;

        // 构建查询
        String whereClause = 'id = ? AND deleted_at IS NULL';
        List<Object?> whereArgs = [documentId];

        // 应用过滤器
        if (filter != null) {
          // 这里实现过滤逻辑
        }

        final documentResult = await _databaseService.query(
          'vector_documents',
          where: whereClause,
          whereArgs: whereArgs,
          limit: 1,
        );

        if (documentResult.isNotEmpty) {
          final document = documentResult.first;

          results.add(
            SearchResult(
              content: document['content'] as String,
              documentId: documentId,
              score: similarity['score'] as double,
              metadata: jsonDecode(document['metadata'] as String? ?? '{}'),
            ),
          );
        }
      }

      return results;
    } catch (e) {
      logger.e('相似性搜索失败: $e');
      return [];
    }
  }

  @override
  Future<void> createCollection(String collection) async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();

      // 检查集合是否已存在
      final existingCollections = await _databaseService.query(
        'vector_collections',
        where: 'name = ?',
        whereArgs: [collection],
      );

      if (existingCollections.isEmpty) {
        // 创建新集合
        await _databaseService.insert('vector_collections', {
          'name': collection,
          'created_at': DateTime.now().toIso8601String(),
        });
      }
    } catch (e) {
      logger.e('创建集合失败: $e');
      throw Exception('创建集合失败: $e');
    }
  }

  @override
  Future<void> deleteCollection(String collection) async {
    try {
      // 标记集合中的所有文档为已删除
      await _databaseService.update(
        'vector_documents',
        {
          'deleted_at': DateTime.now().toIso8601String(),
          'sync_status': 'pending_delete',
        },
        where: 'collection = ?',
        whereArgs: [collection],
      );

      // 标记集合为已删除
      await _databaseService.update(
        'vector_collections',
        {
          'deleted_at': DateTime.now().toIso8601String(),
          'sync_status': 'pending_delete',
        },
        where: 'name = ?',
        whereArgs: [collection],
      );
    } catch (e) {
      logger.e('删除集合失败: $e');
      throw Exception('删除集合失败: $e');
    }
  }

  @override
  Future<List<String>> listCollections() async {
    try {
      // 确保向量表存在
      await _ensureVectorTablesExist();

      final collections = await _databaseService.query(
        'vector_collections',
        where: 'deleted_at IS NULL',
      );

      return collections.map((row) => row['name'] as String).toList();
    } catch (e) {
      logger.e('列出集合失败: $e');
      return [];
    }
  }

  @override
  Future<Embedding?> getCachedEmbedding(String text) async {
    // 检查内存缓存
    if (_embeddingCache.containsKey(text)) {
      return _embeddingCache[text];
    }

    try {
      // 从数据库中查询缓存
      final results = await _databaseService.query(
        'embedding_cache',
        where: 'text_hash = ?',
        whereArgs: [text.hashCode.toString()],
        limit: 1,
      );

      if (results.isNotEmpty) {
        final cachedData = results.first;
        final vector = _decodeVector(cachedData['embedding'] as String);

        final embedding = Embedding(vector: vector, text: text);

        // 添加到内存缓存
        _embeddingCache[text] = embedding;

        return embedding;
      }

      return null;
    } catch (e) {
      logger.w('获取缓存嵌入失败: $e');
      return null;
    }
  }

  @override
  Future<void> cacheEmbedding(String text, Embedding embedding) async {
    try {
      // 添加到内存缓存
      _embeddingCache[text] = embedding;

      // 确保缓存表存在
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS embedding_cache (
          text_hash TEXT PRIMARY KEY,
          text TEXT NOT NULL,
          embedding TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');

      // 存储到数据库
      await _databaseService.insert('embedding_cache', {
        'text_hash': text.hashCode.toString(),
        'text': text,
        'embedding': _encodeVector(embedding.vector),
        'created_at': DateTime.now().toIso8601String(),
      }); // 移除冲突算法参数

      // 清理旧缓存，保留最新的1000条
      await _databaseService.execute('''
        DELETE FROM embedding_cache WHERE rowid NOT IN (
          SELECT rowid FROM embedding_cache ORDER BY created_at DESC LIMIT 1000
        )
      ''');
    } catch (e) {
      logger.w('缓存嵌入失败: $e');
    }
  }

  /// 确保向量表存在
  Future<void> _ensureVectorTablesExist() async {
    try {
      // 创建集合表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_collections (
          name TEXT PRIMARY KEY,
          created_at TEXT NOT NULL,
          deleted_at TEXT,
          sync_status TEXT
        )
      ''');

      // 创建文档表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_documents (
          id TEXT PRIMARY KEY,
          content TEXT NOT NULL,
          collection TEXT NOT NULL,
          metadata TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT,
          deleted_at TEXT,
          sync_status TEXT
        )
      ''');

      // 创建嵌入表
      await _databaseService.execute('''
        CREATE TABLE IF NOT EXISTS vector_embeddings (
          document_id TEXT PRIMARY KEY,
          collection TEXT NOT NULL,
          embedding TEXT NOT NULL,
          dimension INTEGER NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');

      // 创建索引
      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_embeddings_collection ON vector_embeddings (collection)',
      );

      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_documents_collection ON vector_documents (collection)',
      );

      await _databaseService.execute(
        'CREATE INDEX IF NOT EXISTS idx_documents_sync ON vector_documents (sync_status)',
      );
    } catch (e) {
      logger.e('创建向量表失败: $e');
      throw Exception('创建向量表失败: $e');
    }
  }

  /// 编码向量为字符串
  String _encodeVector(List<double> vector) {
    return jsonEncode(vector);
  }

  /// 解码字符串为向量
  List<double> _decodeVector(String encoded) {
    final List<dynamic> data = jsonDecode(encoded);
    return data.map((v) => (v as num).toDouble()).toList();
  }

  /// 计算余弦相似度
  double _cosineSimilarity(List<double> a, List<double> b) {
    if (a.length != b.length) {
      throw Exception('向量维度不匹配');
    }

    double dotProduct = 0.0;
    double normA = 0.0;
    double normB = 0.0;

    for (int i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }

    normA = sqrt(normA);
    normB = sqrt(normB);

    if (normA == 0 || normB == 0) {
      return 0.0;
    }

    return dotProduct / (normA * normB);
  }

  /// 获取待同步的文档
  Future<List<Map<String, dynamic>>> getPendingSyncDocuments() async {
    try {
      return await _databaseService.query(
        'vector_documents',
        where: 'sync_status = ? AND deleted_at IS NULL',
        whereArgs: ['pending'],
      );
    } catch (e) {
      logger.e('获取待同步文档失败: $e');
      return [];
    }
  }

  /// 获取待删除同步的文档
  Future<List<Map<String, dynamic>>> getPendingDeleteDocuments() async {
    try {
      return await _databaseService.query(
        'vector_documents',
        where: 'sync_status = ?',
        whereArgs: ['pending_delete'],
      );
    } catch (e) {
      logger.e('获取待删除同步文档失败: $e');
      return [];
    }
  }

  /// 标记文档为已同步
  Future<void> markDocumentSynced(String documentId) async {
    try {
      await _databaseService.update(
        'vector_documents',
        {'sync_status': 'synced'},
        where: 'id = ?',
        whereArgs: [documentId],
      );
    } catch (e) {
      logger.e('标记文档已同步失败: $e');
    }
  }

  /// 物理删除已同步的删除文档
  Future<void> purgeDeletedSyncedDocuments() async {
    try {
      // 获取待物理删除的文档ID
      final docsToDelete = await _databaseService.query(
        'vector_documents',
        columns: ['id'],
        where: 'sync_status = ? AND deleted_at IS NOT NULL',
        whereArgs: ['synced'],
      );

      for (final doc in docsToDelete) {
        final documentId = doc['id'] as String;

        // 删除嵌入
        await _databaseService.delete(
          'vector_embeddings',
          where: 'document_id = ?',
          whereArgs: [documentId],
        );

        // 删除文档
        await _databaseService.delete(
          'vector_documents',
          where: 'id = ?',
          whereArgs: [documentId],
        );
      }
    } catch (e) {
      logger.e('清除已删除同步文档失败: $e');
    }
  }
}

/// 搜索结果数据类
class SearchResult {
  final String content;
  final String documentId;
  final double score;
  final Map<String, dynamic> metadata;

  SearchResult({
    required this.content,
    required this.documentId,
    required this.score,
    required this.metadata,
  });
}

/// 默认医疗服务API实现
class DefaultMedicalServiceAPI implements MedicalServiceAPI {
  final ApiClient apiClient;

  DefaultMedicalServiceAPI(this.apiClient);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 默认个性化系统实现
class DefaultPersonalizationSystem implements PersonalizationSystem {
  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 运动规划
class DefaultExercisePlanningAgent implements ExercisePlanningAgent {
  final AgentMicrokernel microkernel;
  final AutonomousLearningSystem learningSystem;

  DefaultExercisePlanningAgent(this.microkernel, this.learningSystem);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 医学诊断
class DefaultMedicalDiagnosisAgent implements MedicalDiagnosisAgent {
  final AgentMicrokernel microkernel;
  final MedicalServiceAPI medicalService;

  DefaultMedicalDiagnosisAgent(this.microkernel, this.medicalService);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 心理健康
class DefaultMentalHealthAgent implements MentalHealthAgent {
  final AgentMicrokernel microkernel;
  final AutonomousLearningSystem learningSystem;

  DefaultMentalHealthAgent(this.microkernel, this.learningSystem);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 营养平衡
class DefaultNutritionBalanceAgent implements NutritionBalanceAgent {
  final AgentMicrokernel microkernel;
  final AutonomousLearningSystem learningSystem;

  DefaultNutritionBalanceAgent(this.microkernel, this.learningSystem);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 睡眠优化
class DefaultSleepOptimizationAgent implements SleepOptimizationAgent {
  final AgentMicrokernel microkernel;
  final AutonomousLearningSystem learningSystem;

  DefaultSleepOptimizationAgent(this.microkernel, this.learningSystem);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 专家代理实现类 - 知识图谱
class DefaultKnowledgeGraphAgent implements KnowledgeGraphAgent {
  final AgentMicrokernel microkernel;
  final KnowledgeGraphRepository repository;

  DefaultKnowledgeGraphAgent(this.microkernel, this.repository);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 供应链代理实现类 - 农业
class DefaultAgricultureAgent implements AgricultureAgent {
  final AgentMicrokernel microkernel;
  final AutonomousLearningSystem learningSystem;

  DefaultAgricultureAgent(this.microkernel, this.learningSystem);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// 健康数据本地数据源实现
class DefaultHealthDataLocalSource implements HealthDataLocalSource {
  final DatabaseHelper databaseHelper;
  final Logger logger;

  DefaultHealthDataLocalSource(this.databaseHelper, this.logger);

  // 实现接口...
  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

/// DefaultAgentRegistry扩展，添加设置工厂方法
extension AgentRegistryExtension on DefaultAgentRegistry {
  void setFactory(AgentFactory factory) {
    // 实现方法，根据实际情况调整
  }
}
