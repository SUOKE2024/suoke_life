import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';
import 'package:suoke_life/core/di/injection.dart';
import 'package:suoke_life/core/database/local/database_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized(); // 确保 Flutter 绑定已初始化

  setUpAll(() {
    configureDependencies(); // 配置依赖注入
  });

  tearDownAll(() {
    GetIt.instance.reset(); // 在所有测试结束后重置 GetIt 实例
  });

  group('DatabaseService', () {
    test('DatabaseService can be successfully resolved from GetIt', () {
      // 从 GetIt 容器中解析 DatabaseService 实例
      final databaseService = GetIt.instance.get<DatabaseService>();

      // 断言 databaseService 实例不为空，表示成功解析
      expect(databaseService, isNotNull);
      expect(databaseService, isInstanceOf<DatabaseService>());
    });
  });
} 