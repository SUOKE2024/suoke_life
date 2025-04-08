import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/knowledge_remote_datasource.dart';
import 'package:suoke_life/data/models/knowledge_model.dart';
import 'package:suoke_life/domain/repositories/knowledge_repository.dart';

/// 知识存储库实现
class KnowledgeRepositoryImpl implements KnowledgeRepository {
  final KnowledgeRemoteDataSource remoteDataSource;
  final NetworkInfo networkInfo;
  
  KnowledgeRepositoryImpl({
    required this.remoteDataSource,
    required this.networkInfo,
  });
  
  @override
  Future<Either<Failure, List<KnowledgeNodeModel>>> getNodes({
    String? query,
    List<String>? tags,
    List<String>? types,
    int page = 1,
    int pageSize = 20
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final nodes = await remoteDataSource.getNodes(
          query: query,
          tags: tags,
          types: types,
          page: page,
          pageSize: pageSize
        );
        return Right(nodes);
      } on NetworkException catch (e) {
        return Left(NetworkFailure(e.message));
      } on UnauthorizedException catch (e) {
        return Left(AuthFailure(e.message));
      } catch (e) {
        return Left(ServerFailure(e.toString()));
      }
    } else {
      return Left(NetworkFailure('网络连接不可用'));
    }
  }
  
  @override
  Future<Either<Failure, KnowledgeNodeModel>> getNodeById(String nodeId) async {
    if (await networkInfo.isConnected) {
      try {
        final node = await remoteDataSource.getNodeById(nodeId);
        return Right(node);
      } on NetworkException catch (e) {
        return Left(NetworkFailure(e.message));
      } on UnauthorizedException catch (e) {
        return Left(AuthFailure(e.message));
      } on NotFoundException catch (e) {
        return Left(NotFoundFailure(e.message));
      } catch (e) {
        return Left(ServerFailure(e.toString()));
      }
    } else {
      return Left(NetworkFailure('网络连接不可用'));
    }
  }
  
  @override
  Future<Either<Failure, List<KnowledgeRelationModel>>> getNodeRelations(String nodeId) async {
    if (await networkInfo.isConnected) {
      try {
        final relations = await remoteDataSource.getNodeRelations(nodeId);
        return Right(relations);
      } on NetworkException catch (e) {
        return Left(NetworkFailure(e.message));
      } on UnauthorizedException catch (e) {
        return Left(AuthFailure(e.message));
      } catch (e) {
        return Left(ServerFailure(e.toString()));
      }
    } else {
      return Left(NetworkFailure('网络连接不可用'));
    }
  }
  
  @override
  Future<Either<Failure, List<KnowledgeNodeModel>>> searchNodes(String query) async {
    if (await networkInfo.isConnected) {
      try {
        final results = await remoteDataSource.searchNodes(query);
        return Right(results);
      } on NetworkException catch (e) {
        return Left(NetworkFailure(e.message));
      } on UnauthorizedException catch (e) {
        return Left(AuthFailure(e.message));
      } catch (e) {
        return Left(ServerFailure(e.toString()));
      }
    } else {
      return Left(NetworkFailure('网络连接不可用'));
    }
  }
} 