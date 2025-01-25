import 'package:injectable/injectable.dart';
import '../../domain/services/suoke_service.dart';

@LazySingleton(as: SuokeService)
class SuokeServiceImpl implements SuokeService {
  const SuokeServiceImpl();

  @override
  Future<void> initialize() async {
    // 实现初始化逻辑
  }
} 