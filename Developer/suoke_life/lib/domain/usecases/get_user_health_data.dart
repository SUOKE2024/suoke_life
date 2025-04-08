import 'package:dartz/dartz.dart';
import '../repositories/user_repository.dart';
import '../entities/health_data.dart';
import '../../core/error/failures.dart';
import '../../core/usecases/usecase.dart';

/// 获取用户健康数据参数
class GetUserHealthDataParams {
  /// 用户ID
  final String userId;
  
  /// 时间段（可选，如'daily', 'weekly', 'monthly'）
  final String? period;

  /// 构造函数
  const GetUserHealthDataParams({
    required this.userId,
    this.period,
  });
  
  @override
  String toString() => 'GetUserHealthDataParams(userId: $userId, period: $period)';
}

/// 获取用户健康数据用例
class GetUserHealthData implements UseCase<HealthData, GetUserHealthDataParams> {
  /// 用户存储库
  final UserRepository repository;

  /// 构造函数
  GetUserHealthData(this.repository);

  @override
  Future<Either<Failure, HealthData>> call(GetUserHealthDataParams params) async {
    return await repository.getUserHealthData(params.userId, period: params.period);
  }
} 