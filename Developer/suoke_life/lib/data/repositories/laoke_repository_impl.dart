import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/exceptions.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/laoke_remote_datasource.dart';
import 'package:suoke_life/data/models/laoke/knowledge_article_model.dart';
import 'package:suoke_life/data/models/laoke/knowledge_category_model.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_article.dart';
import 'package:suoke_life/domain/entities/laoke/knowledge_category.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

class LaokeRepositoryImpl implements LaokeRepository {
  final LaokeRemoteDataSource remoteDataSource;
  final NetworkInfo networkInfo;

  LaokeRepositoryImpl({
    required this.remoteDataSource,
    required this.networkInfo,
  });

  @override
  Future<Either<Failure, Map<String, dynamic>>> getServiceStatus() async {
    if (await networkInfo.isConnected) {
      try {
        final status = await remoteDataSource.getServiceStatus();
        return Right(status);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '服务器错误',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, List<KnowledgeCategory>>> getKnowledgeCategories() async {
    if (await networkInfo.isConnected) {
      try {
        final categoriesJson = await remoteDataSource.getKnowledgeCategories();
        final categories = categoriesJson
            .map((categoryJson) => KnowledgeCategoryModel.fromJson(categoryJson))
            .toList();
        return Right(categories);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取知识分类失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> getKnowledgeArticles({
    String? categoryId,
    int page = 1,
    int limit = 10,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getKnowledgeArticles(
          categoryId: categoryId,
          page: page,
          limit: limit,
        );
        return Right(result);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取知识文章失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, KnowledgeArticle>> getKnowledgeArticleById(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final articleJson = await remoteDataSource.getKnowledgeArticleById(id);
        final article = KnowledgeArticleModel.fromJson(articleJson);
        return Right(article);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取知识文章详情失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> getTrainingCourses({
    String? categoryId,
    String? level,
    int page = 1,
    int limit = 10,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getTrainingCourses(
          categoryId: categoryId,
          level: level,
          page: page,
          limit: limit,
        );
        return Right(result);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取培训课程失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> getTrainingCourseById(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getTrainingCourseById(id);
        return Right(result);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取培训课程详情失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> getBlogPosts({
    String? authorId,
    String? categoryId,
    String? tag,
    String? status,
    int page = 1,
    int limit = 10,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getBlogPosts(
          authorId: authorId,
          categoryId: categoryId,
          tag: tag,
          status: status,
          page: page,
          limit: limit,
        );
        return Right(result);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取博客文章失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, Map<String, dynamic>>> getBlogPostById(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final result = await remoteDataSource.getBlogPostById(id);
        return Right(result);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '获取博客文章详情失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }

  @override
  Future<Either<Failure, String>> textToSpeech(
    String text, {
    String? voiceId,
    Map<String, dynamic>? options,
  }) async {
    if (await networkInfo.isConnected) {
      try {
        final audioData = await remoteDataSource.textToSpeech(
          text,
          voiceId: voiceId,
          options: options,
        );
        return Right(audioData);
      } on ServerException catch (e) {
        return Left(ServerFailure(
          message: e.message ?? '文字转语音失败',
          statusCode: e.statusCode,
        ));
      } catch (e) {
        return Left(ServerFailure(message: e.toString()));
      }
    } else {
      return Left(NetworkFailure(message: '网络连接不可用'));
    }
  }
} 