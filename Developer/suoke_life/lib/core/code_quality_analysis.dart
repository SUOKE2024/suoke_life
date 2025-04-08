// 自定义静态分析规则
import 'package:meta/meta.dart';

@immutable
class CodeQualityRules {
  static const Map<String, dynamic> analysisOptions = {
    'analyzer': {
      'errors': {
        'missing_required_param': 'error',
        'missing_return': 'error',
      },
      'language': {
        'strict-raw-types': true,
        'strict-inference': true
      }
    },
    'linter': {
      'rules': [
        'avoid_print',
        'prefer_const_constructors',
        'unnecessary_nullable_for_final_variables',
      ]
    }
  };

  static void apply() {
    // 应用静态分析规则
    // 在main.dart初始化时调用
  }
}