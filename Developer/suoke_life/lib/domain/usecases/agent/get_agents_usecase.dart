import 'package:dartz/dartz.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/data/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';

/// 获取智能体列表用例
class GetAgentsUseCase implements UseCase<List<AgentModel>, NoParams> {
  final AgentRepository repository;

  GetAgentsUseCase(this.repository);

  @override
  Future<Either<Failure, List<AgentModel>>> call(NoParams params) {
    return repository.getAgents();
  }
}