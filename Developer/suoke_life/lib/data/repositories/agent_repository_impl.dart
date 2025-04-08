import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/network/network_info.dart';
import 'package:suoke_life/data/datasources/remote/agent_remote_datasource.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/data/models/session_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 智能体存储库实现
class AgentRepositoryImpl implements AgentRepository {
  final AgentRemoteDataSource remoteDataSource;
  final NetworkInfo networkInfo;
  
  AgentRepositoryImpl({
    required this.remoteDataSource,
    required this.networkInfo,
  });
  
  @override
  Future<Either<Failure, List<AgentModel>>> getAgents() async {
    if (await networkInfo.isConnected) {
      try {
        final agents = await remoteDataSource.getAgents();
        return Right(agents);
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
  Future<Either<Failure, AgentModel>> getAgentById(String agentId) async {
    if (await networkInfo.isConnected) {
      try {
        final agent = await remoteDataSource.getAgentById(agentId);
        return Right(agent);
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
  Future<Either<Failure, MessageModel>> sendMessage(String agentId, String message, {String? sessionId}) async {
    if (await networkInfo.isConnected) {
      try {
        final response = await remoteDataSource.sendMessage(agentId, message, sessionId: sessionId);
        return Right(response);
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
  Stream<Either<Failure, MessageModel>> streamFromAgent(String agentId, String message, {String? sessionId}) async* {
    if (await networkInfo.isConnected) {
      try {
        final stream = remoteDataSource.streamFromAgent(agentId, message, sessionId: sessionId);
        
        await for (final response in stream) {
          yield Right(response);
        }
      } on NetworkException catch (e) {
        yield Left(NetworkFailure(e.message));
      } on UnauthorizedException catch (e) {
        yield Left(AuthFailure(e.message));
      } catch (e) {
        yield Left(ServerFailure(e.toString()));
      }
    } else {
      yield Left(NetworkFailure('网络连接不可用'));
    }
  }
  
  @override
  Future<Either<Failure, List<SessionModel>>> getAgentSessions(String agentId) async {
    if (await networkInfo.isConnected) {
      try {
        final sessions = await remoteDataSource.getAgentSessions(agentId);
        return Right(sessions);
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
  Future<Either<Failure, SessionModel>> createSession(String agentId, String title) async {
    if (await networkInfo.isConnected) {
      try {
        final session = await remoteDataSource.createSession(agentId, title);
        return Right(session);
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
  Future<Either<Failure, List<MessageModel>>> getSessionMessages(String sessionId) async {
    if (await networkInfo.isConnected) {
      try {
        final messages = await remoteDataSource.getSessionMessages(sessionId);
        return Right(messages);
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