import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';

import '../../core/network/api_client.dart';
import '../../core/network/network_info.dart';
import '../../data/datasources/knowledge_data_source.dart';
import '../../data/datasources/local/knowledge_local_data_source.dart';
import '../../data/datasources/remote/knowledge_remote_data_source.dart';
import '../../data/repositories/knowledge_repository_impl.dart';
import '../../domain/entities/knowledge_node.dart';
import '../../domain/repositories/knowledge_repository.dart';
import 'core_providers.dart';

/// 知识图谱本地数据源提供者
final knowledgeLocalDataSourceProvider = Provider<KnowledgeDataSource>((ref) {
  final databaseHelper = ref.watch(databaseHelperProvider);
  final logger = ref.watch(loggerProvider);
  
  return KnowledgeLocalDataSource(
    databaseHelper: databaseHelper,
    logger: logger,
  );
});

/// 知识图谱远程数据源提供者
final knowledgeRemoteDataSourceProvider = Provider<KnowledgeDataSource>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  final logger = ref.watch(loggerProvider);
  
  return KnowledgeRemoteDataSource(
    apiClient: apiClient,
    networkInfo: networkInfo,
    logger: logger,
  );
});

/// 知识图谱仓库提供者
final knowledgeRepositoryProvider = Provider<KnowledgeRepository>((ref) {
  final remoteDataSource = ref.watch(knowledgeRemoteDataSourceProvider);
  final localDataSource = ref.watch(knowledgeLocalDataSourceProvider);
  final networkInfo = ref.watch(networkInfoProvider);
  final logger = ref.watch(loggerProvider);
  
  return KnowledgeRepositoryImpl(
    remoteDataSource: remoteDataSource,
    localDataSource: localDataSource,
    networkInfo: networkInfo,
    logger: logger,
  );
});

/// 所有知识节点提供者
final allNodesProvider = FutureProvider<List<KnowledgeNode>>((ref) async {
  final repository = ref.watch(knowledgeRepositoryProvider);
  final result = await repository.getAllNodes();
  return result.fold(
    (failure) => throw Exception(failure.message),
    (nodes) => nodes,
  );
});

/// 按类型获取知识节点提供者
final nodesByTypeProvider = FutureProvider.family<List<KnowledgeNode>, String>((ref, type) async {
  final repository = ref.watch(knowledgeRepositoryProvider);
  final result = await repository.getNodesByType(type);
  return result.fold(
    (failure) => throw Exception(failure.message),
    (nodes) => nodes,
  );
});

/// 知识图谱搜索提供者
final knowledgeSearchProvider = FutureProvider.family<List<KnowledgeNode>, String>((ref, query) async {
  final repository = ref.watch(knowledgeRepositoryProvider);
  final result = await repository.searchNodes(query);
  return result.fold(
    (failure) => throw Exception(failure.message),
    (nodes) => nodes,
  );
});

/// 知识图谱统计信息提供者
final knowledgeStatisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final repository = ref.watch(knowledgeRepositoryProvider);
  final result = await repository.getKnowledgeGraphStatistics();
  return result.fold(
    (failure) => throw Exception(failure.message),
    (statistics) => statistics,
  );
}); 