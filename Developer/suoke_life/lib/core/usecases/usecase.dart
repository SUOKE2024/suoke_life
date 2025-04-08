import 'package:dartz/dartz.dart';
import '../error/failures.dart';

/// 用例基类
///
/// [Type] 返回的数据类型
/// [Params] 用例参数类型
abstract class UseCase<Type, Params> {
  /// 执行用例
  ///
  /// 返回Either包装的结果：失败或成功
  Future<Either<Failure, Type>> call(Params params);
}

/// 流式用例基类
///
/// [Type] 返回的数据类型
/// [Params] 用例参数类型
abstract class StreamUseCase<Type, Params> {
  /// 执行用例
  ///
  /// 返回Either包装的结果流：失败或成功
  Stream<Either<Failure, Type>> call(Params params);
}

/// 无参数用例
class NoParams {
  @override
  String toString() {
    return 'NoParams()';
  }
} 