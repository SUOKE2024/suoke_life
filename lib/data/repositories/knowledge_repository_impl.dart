import 'package:dartz/dartz.dart';
import 'package:logger/logger.dart';

import '../../core/error/exceptions.dart';
import '../../core/error/failures.dart';
import '../../core/network/network_info.dart';
import '../../domain/entities/knowledge_node.dart';
import '../../domain/entities/node_relation.dart';
import '../../domain/repositories/knowledge_repository.dart';
import '../datasources/knowledge_data_source.dart';
import '../models/knowledge_node_model.dart';
import '../models/node_relation_model.dart';

/// 知识图谱仓库实现
class KnowledgeRepositoryImpl implements KnowledgeRepository {
  final KnowledgeDataSource remoteDataSource;
  final KnowledgeDataSource localDataSource;
  final NetworkInfo networkInfo;
  final Logger logger;
  
  KnowledgeRepositoryImpl({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.networkInfo,
    required this.logger,
  });
  
  @override
  Future<Either<Failure, List<KnowledgeNode>>> getAllNodes() async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteNodes = await remoteDataSource.getAllNodes();
          
          // 缓存到本地
          for (final node in remoteNodes) {
            try {
              await localDataSource.saveNode(node);
            } catch (_) {
              // 忽略本地缓存错误
            }
          }
          
          // 返回远程数据
          return Right(remoteNodes.map((model) => _modelToEntity(model)).toList());
        } on ServerException catch (e) {
          logger.e('从远程获取知识节点失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localNodes = await localDataSource.getAllNodes();
      return Right(localNodes.map((model) => _modelToEntity(model)).toList());
    } on CacheException catch (e) {
      logger.e('从本地获取知识节点失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('获取所有知识节点失败', error: e);
      return Left(InternalFailure(message: '获取所有知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, KnowledgeNode>> getNodeById(String nodeId) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteNode = await remoteDataSource.getNodeById(nodeId);
          
          // 缓存到本地
          try {
            await localDataSource.saveNode(remoteNode);
          } catch (_) {
            // 忽略本地缓存错误
          }
          
          // 返回远程数据
          return Right(_modelToEntity(remoteNode));
        } on ServerException catch (e) {
          logger.e('从远程获取知识节点失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localNode = await localDataSource.getNodeById(nodeId);
      return Right(_modelToEntity(localNode));
    } on CacheException catch (e) {
      logger.e('从本地获取知识节点失败', error: e);
      return Left(CacheFailure(message: e.message));
    } on ServerException catch (e) {
      if (e.statusCode == 404) {
        return Left(NotFoundFailure(message: '知识节点不存在'));
      }
      return Left(ServerFailure(
        message: e.message,
        statusCode: e.statusCode,
      ));
    } catch (e) {
      logger.e('获取知识节点失败', error: e);
      return Left(InternalFailure(message: '获取知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<KnowledgeNode>>> getNodesByType(String type) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteNodes = await remoteDataSource.getNodesByType(type);
          
          // 缓存到本地
          for (final node in remoteNodes) {
            try {
              await localDataSource.saveNode(node);
            } catch (_) {
              // 忽略本地缓存错误
            }
          }
          
          // 返回远程数据
          return Right(remoteNodes.map((model) => _modelToEntity(model)).toList());
        } on ServerException catch (e) {
          logger.e('从远程获取类型知识节点失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localNodes = await localDataSource.getNodesByType(type);
      return Right(localNodes.map((model) => _modelToEntity(model)).toList());
    } on CacheException catch (e) {
      logger.e('从本地获取类型知识节点失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('获取类型知识节点失败', error: e);
      return Left(InternalFailure(message: '获取类型知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<KnowledgeNode>>> searchNodes(
    String query, {
    List<String>? types,
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程搜索
          final remoteNodes = await remoteDataSource.searchNodes(
            query,
            types: types,
            limit: limit,
            offset: offset,
          );
          
          // 返回远程数据
          return Right(remoteNodes.map((model) => _modelToEntity(model)).toList());
        } on ServerException catch (e) {
          logger.e('从远程搜索知识节点失败，尝试使用本地数据', error: e);
          // 远程搜索失败，回退到本地搜索
        }
      }
      
      // 从本地搜索
      final localNodes = await localDataSource.searchNodes(
        query,
        types: types,
        limit: limit,
        offset: offset,
      );
      return Right(localNodes.map((model) => _modelToEntity(model)).toList());
    } on CacheException catch (e) {
      logger.e('从本地搜索知识节点失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('搜索知识节点失败', error: e);
      return Left(InternalFailure(message: '搜索知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<KnowledgeNode>>> semanticSearchNodes(
    List<double> queryEmbedding, {
    List<String>? types,
    int limit = 20,
    double minScore = 0.6,
  }) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (!isConnected) {
        return Left(NetworkFailure(message: '无网络连接，无法执行语义搜索'));
      }
      
      try {
        // 尝试从远程语义搜索
        final remoteNodes = await remoteDataSource.semanticSearchNodes(
          queryEmbedding,
          types: types,
          limit: limit,
          minScore: minScore,
        );
        
        // 返回远程数据
        return Right(remoteNodes.map((model) => _modelToEntity(model)).toList());
      } on ServerException catch (e) {
        logger.e('从远程语义搜索知识节点失败', error: e);
        return Left(ServerFailure(
          message: e.message,
          statusCode: e.statusCode,
        ));
      }
    } catch (e) {
      logger.e('语义搜索知识节点失败', error: e);
      return Left(InternalFailure(message: '语义搜索知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, KnowledgeNode>> saveNode(KnowledgeNode node) async {
    try {
      final isConnected = await networkInfo.isConnected;
      final nodeModel = _entityToModel(node);
      
      if (isConnected) {
        try {
          // 尝试保存到远程
          final remoteSavedNode = await remoteDataSource.saveNode(nodeModel);
          
          // 同步到本地
          try {
            await localDataSource.saveNode(remoteSavedNode);
          } catch (_) {
            // 忽略本地保存错误
          }
          
          // 返回远程保存的数据
          return Right(_modelToEntity(remoteSavedNode));
        } on ServerException catch (e) {
          logger.e('保存知识节点到远程失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      } else {
        // 无网络连接，保存到本地
        final localSavedNode = await localDataSource.saveNode(nodeModel);
        return Right(_modelToEntity(localSavedNode));
      }
    } on CacheException catch (e) {
      logger.e('保存知识节点到本地失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('保存知识节点失败', error: e);
      return Left(InternalFailure(message: '保存知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, KnowledgeNode>> updateNode(KnowledgeNode node) async {
    try {
      final isConnected = await networkInfo.isConnected;
      final nodeModel = _entityToModel(node);
      
      if (isConnected) {
        try {
          // 尝试更新远程
          final remoteUpdatedNode = await remoteDataSource.updateNode(nodeModel);
          
          // 同步到本地
          try {
            await localDataSource.updateNode(remoteUpdatedNode);
          } catch (_) {
            // 忽略本地更新错误
          }
          
          // 返回远程更新的数据
          return Right(_modelToEntity(remoteUpdatedNode));
        } on ServerException catch (e) {
          logger.e('更新知识节点到远程失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      } else {
        // 无网络连接，更新本地
        final localUpdatedNode = await localDataSource.updateNode(nodeModel);
        return Right(_modelToEntity(localUpdatedNode));
      }
    } on CacheException catch (e) {
      logger.e('更新知识节点到本地失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('更新知识节点失败', error: e);
      return Left(InternalFailure(message: '更新知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, void>> deleteNode(String nodeId) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程删除
          await remoteDataSource.deleteNode(nodeId);
        } on ServerException catch (e) {
          logger.e('从远程删除知识节点失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      }
      
      // 从本地删除
      await localDataSource.deleteNode(nodeId);
      return const Right(null);
    } on CacheException catch (e) {
      logger.e('从本地删除知识节点失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('删除知识节点失败', error: e);
      return Left(InternalFailure(message: '删除知识节点失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<NodeRelation>>> getNodeRelations(String nodeId) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteRelations = await remoteDataSource.getNodeRelations(nodeId);
          
          // 缓存到本地
          for (final relation in remoteRelations) {
            try {
              await localDataSource.saveRelation(relation);
            } catch (_) {
              // 忽略本地缓存错误
            }
          }
          
          // 返回远程数据
          return Right(remoteRelations.map((model) => _relationModelToEntity(model)).toList());
        } on ServerException catch (e) {
          logger.e('从远程获取节点关系失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localRelations = await localDataSource.getNodeRelations(nodeId);
      return Right(localRelations.map((model) => _relationModelToEntity(model)).toList());
    } on CacheException catch (e) {
      logger.e('从本地获取节点关系失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('获取节点关系失败', error: e);
      return Left(InternalFailure(message: '获取节点关系失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<NodeRelation>>> getRelationsByType(String relationType) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteRelations = await remoteDataSource.getRelationsByType(relationType);
          
          // 缓存到本地
          for (final relation in remoteRelations) {
            try {
              await localDataSource.saveRelation(relation);
            } catch (_) {
              // 忽略本地缓存错误
            }
          }
          
          // 返回远程数据
          return Right(remoteRelations.map((model) => _relationModelToEntity(model)).toList());
        } on ServerException catch (e) {
          logger.e('从远程获取关系类型失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localRelations = await localDataSource.getRelationsByType(relationType);
      return Right(localRelations.map((model) => _relationModelToEntity(model)).toList());
    } on CacheException catch (e) {
      logger.e('从本地获取关系类型失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('获取关系类型失败', error: e);
      return Left(InternalFailure(message: '获取关系类型失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, NodeRelation>> saveRelation(NodeRelation relation) async {
    try {
      final isConnected = await networkInfo.isConnected;
      final relationModel = _entityToRelationModel(relation);
      
      if (isConnected) {
        try {
          // 尝试保存到远程
          final remoteSavedRelation = await remoteDataSource.saveRelation(relationModel);
          
          // 同步到本地
          try {
            await localDataSource.saveRelation(remoteSavedRelation);
          } catch (_) {
            // 忽略本地保存错误
          }
          
          // 返回远程保存的数据
          return Right(_relationModelToEntity(remoteSavedRelation));
        } on ServerException catch (e) {
          logger.e('保存节点关系到远程失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      } else {
        // 无网络连接，保存到本地
        final localSavedRelation = await localDataSource.saveRelation(relationModel);
        return Right(_relationModelToEntity(localSavedRelation));
      }
    } on CacheException catch (e) {
      logger.e('保存节点关系到本地失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('保存节点关系失败', error: e);
      return Left(InternalFailure(message: '保存节点关系失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, NodeRelation>> updateRelation(NodeRelation relation) async {
    try {
      final isConnected = await networkInfo.isConnected;
      final relationModel = _entityToRelationModel(relation);
      
      if (isConnected) {
        try {
          // 尝试更新远程
          final remoteUpdatedRelation = await remoteDataSource.updateRelation(relationModel);
          
          // 同步到本地
          try {
            await localDataSource.updateRelation(remoteUpdatedRelation);
          } catch (_) {
            // 忽略本地更新错误
          }
          
          // 返回远程更新的数据
          return Right(_relationModelToEntity(remoteUpdatedRelation));
        } on ServerException catch (e) {
          logger.e('更新节点关系到远程失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      } else {
        // 无网络连接，更新本地
        final localUpdatedRelation = await localDataSource.updateRelation(relationModel);
        return Right(_relationModelToEntity(localUpdatedRelation));
      }
    } on CacheException catch (e) {
      logger.e('更新节点关系到本地失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('更新节点关系失败', error: e);
      return Left(InternalFailure(message: '更新节点关系失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, void>> deleteRelation(String relationId) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程删除
          await remoteDataSource.deleteRelation(relationId);
        } on ServerException catch (e) {
          logger.e('从远程删除节点关系失败', error: e);
          return Left(ServerFailure(
            message: e.message,
            statusCode: e.statusCode,
          ));
        }
      }
      
      // 从本地删除
      await localDataSource.deleteRelation(relationId);
      return const Right(null);
    } on CacheException catch (e) {
      logger.e('从本地删除节点关系失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('删除节点关系失败', error: e);
      return Left(InternalFailure(message: '删除节点关系失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, Map<String, dynamic>>> getKnowledgeGraphStatistics() async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (isConnected) {
        try {
          // 尝试从远程获取
          final remoteStats = await remoteDataSource.getKnowledgeGraphStatistics();
          return Right(remoteStats);
        } on ServerException catch (e) {
          logger.e('从远程获取知识图谱统计失败，尝试使用本地数据', error: e);
          // 远程获取失败，回退到本地数据
        }
      }
      
      // 从本地获取
      final localStats = await localDataSource.getKnowledgeGraphStatistics();
      return Right(localStats);
    } on CacheException catch (e) {
      logger.e('从本地获取知识图谱统计失败', error: e);
      return Left(CacheFailure(message: e.message));
    } catch (e) {
      logger.e('获取知识图谱统计失败', error: e);
      return Left(InternalFailure(message: '获取知识图谱统计失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, List<double>>> generateNodeEmbedding(
    String content, {
    String title = '',
    String type = '',
  }) async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (!isConnected) {
        return Left(NetworkFailure(message: '无网络连接，无法生成嵌入向量'));
      }
      
      try {
        // 从远程生成嵌入向量
        final embedding = await remoteDataSource.generateNodeEmbedding(
          content,
          title: title,
          type: type,
        );
        
        return Right(embedding);
      } on ServerException catch (e) {
        logger.e('生成节点嵌入向量失败', error: e);
        return Left(ServerFailure(
          message: e.message,
          statusCode: e.statusCode,
        ));
      }
    } catch (e) {
      logger.e('生成节点嵌入向量失败', error: e);
      return Left(InternalFailure(message: '生成节点嵌入向量失败: $e'));
    }
  }
  
  @override
  Future<Either<Failure, bool>> syncKnowledgeGraph() async {
    try {
      final isConnected = await networkInfo.isConnected;
      
      if (!isConnected) {
        return Left(NetworkFailure(message: '无网络连接，无法同步知识图谱'));
      }
      
      try {
        // 同步知识图谱
        final success = await remoteDataSource.syncKnowledgeGraph();
        
        return Right(success);
      } on ServerException catch (e) {
        logger.e('同步知识图谱失败', error: e);
        return Left(ServerFailure(
          message: e.message,
          statusCode: e.statusCode,
        ));
      }
    } catch (e) {
      logger.e('同步知识图谱失败', error: e);
      return Left(InternalFailure(message: '同步知识图谱失败: $e'));
    }
  }
  
  // 辅助方法：将模型转换为实体
  KnowledgeNode _modelToEntity(KnowledgeNodeModel model) {
    return KnowledgeNode(
      id: model.id,
      type: model.type,
      title: model.title,
      description: model.description,
      content: model.content,
      createdAt: DateTime.fromMillisecondsSinceEpoch(model.createdAt),
      updatedAt: DateTime.fromMillisecondsSinceEpoch(model.updatedAt),
      metadata: model.metadata != null ? _jsonToMap(model.metadata!) : null,
      embedding: model.embedding,
      language: model.language,
    );
  }
  
  // 辅助方法：将实体转换为模型
  KnowledgeNodeModel _entityToModel(KnowledgeNode entity) {
    return KnowledgeNodeModel(
      id: entity.id,
      type: entity.type,
      title: entity.title,
      description: entity.description,
      content: entity.content,
      createdAt: entity.createdAt.millisecondsSinceEpoch,
      updatedAt: entity.updatedAt.millisecondsSinceEpoch,
      metadata: entity.metadata != null ? _mapToJson(entity.metadata!) : null,
      embedding: entity.embedding,
      language: entity.language,
    );
  }
  
  // 辅助方法：将关系模型转换为实体
  NodeRelation _relationModelToEntity(NodeRelationModel model) {
    return NodeRelation(
      id: model.id,
      sourceNodeId: model.sourceNodeId,
      targetNodeId: model.targetNodeId,
      relationType: model.relationType,
      weight: model.weight,
      metadata: model.metadata != null ? _jsonToMap(model.metadata!) : null,
    );
  }
  
  // 辅助方法：将关系实体转换为模型
  NodeRelationModel _entityToRelationModel(NodeRelation entity) {
    return NodeRelationModel(
      id: entity.id,
      sourceNodeId: entity.sourceNodeId,
      targetNodeId: entity.targetNodeId,
      relationType: entity.relationType,
      weight: entity.weight,
      metadata: entity.metadata != null ? _mapToJson(entity.metadata!) : null,
    );
  }
  
  // 辅助方法：将JSON字符串转换为Map
  Map<String, dynamic> _jsonToMap(String json) {
    try {
      return Map<String, dynamic>.from(Uri.decodeComponent(json) as Map);
    } catch (_) {
      return {'data': json};
    }
  }
  
  // 辅助方法：将Map转换为JSON字符串
  String _mapToJson(Map<String, dynamic> map) {
    try {
      return Uri.encodeComponent(map.toString());
    } catch (_) {
      return map.toString();
    }
  }
}

// 未找到资源错误
class NotFoundFailure extends Failure {
  const NotFoundFailure({
    required String message,
    String? code,
  }) : super(
    message: message,
    code: code,
  );
} 
