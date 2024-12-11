import 'dart:async';
import 'dart:convert';
import 'package:crypto/crypto.dart';

/// 数据价值分析器
class ValueAnalyzer {
  /// 数据价值评分阈值
  static const double _valueThreshold = 0.6;
  
  /// 数据新鲜度权重
  static const double _freshnessWeight = 0.3;
  
  /// 数据完整性权重
  static const double _completenessWeight = 0.2;
  
  /// 数据关联性权重
  static const double _correlationWeight = 0.2;
  
  /// 数据使用频率权重
  static const double _frequencyWeight = 0.3;
  
  /// 分析数据价值
  Future<DataValue> analyzeValue(dynamic data, DataContext context) async {
    try {
      // 计算数据新鲜度得分
      final freshnessScore = _calculateFreshnessScore(context.timestamp);
      
      // 计算数据完整性得分
      final completenessScore = _calculateCompletenessScore(data);
      
      // 计算数据关联性得分
      final correlationScore = await _calculateCorrelationScore(data, context);
      
      // 计算使用频率得分
      final frequencyScore = _calculateFrequencyScore(context.accessCount);
      
      // 计算综合得分
      final totalScore = (freshnessScore * _freshnessWeight) +
          (completenessScore * _completenessWeight) +
          (correlationScore * _correlationWeight) +
          (frequencyScore * _frequencyWeight);
      
      // 生成数据指纹
      final fingerprint = await _generateFingerprint(data);
      
      return DataValue(
        score: totalScore,
        isValuable: totalScore >= _valueThreshold,
        metrics: ValueMetrics(
          freshness: freshnessScore,
          completeness: completenessScore,
          correlation: correlationScore,
          frequency: frequencyScore,
        ),
        fingerprint: fingerprint,
      );
    } catch (e) {
      print('Failed to analyze data value: $e');
      return DataValue.empty();
    }
  }
  
  /// 计算数据新鲜度得分
  double _calculateFreshnessScore(DateTime timestamp) {
    final age = DateTime.now().difference(timestamp).inHours;
    
    // 24小时内的数据得分较高
    if (age <= 24) {
      return 1.0 - (age / 24);
    }
    
    // 24小时到7天内的数据得分递减
    if (age <= 168) {
      return 0.7 * (1.0 - ((age - 24) / 144));
    }
    
    // 7天以上的数据得分较低
    return 0.3 * (1.0 - (min(age - 168, 720) / 720));
  }
  
  /// 计算数据完整性得分
  double _calculateCompletenessScore(dynamic data) {
    if (data == null) return 0.0;
    
    if (data is Map) {
      // 检查必填字段是否完整
      final requiredFields = _getRequiredFields(data);
      final existingFields = data.keys.where((key) => data[key] != null).length;
      return existingFields / requiredFields.length;
    }
    
    if (data is List) {
      // 检查列表数据的完整性
      if (data.isEmpty) return 0.0;
      final nonNullItems = data.where((item) => item != null).length;
      return nonNullItems / data.length;
    }
    
    // 简单数据类型，非空即完整
    return data.toString().isNotEmpty ? 1.0 : 0.0;
  }
  
  /// 计算数据关联性得分
  Future<double> _calculateCorrelationScore(dynamic data, DataContext context) async {
    if (data == null || context.relatedData.isEmpty) return 0.0;
    
    try {
      // 计算与相关数据的相似度
      double totalSimilarity = 0.0;
      
      for (final relatedItem in context.relatedData) {
        final similarity = await _calculateSimilarity(data, relatedItem);
        totalSimilarity += similarity;
      }
      
      return totalSimilarity / context.relatedData.length;
    } catch (e) {
      print('Failed to calculate correlation score: $e');
      return 0.0;
    }
  }
  
  /// 计算使用频率得分
  double _calculateFrequencyScore(int accessCount) {
    // 根据访问次数计算使用频率得分
    if (accessCount == 0) return 0.0;
    if (accessCount >= 100) return 1.0;
    
    return accessCount / 100;
  }
  
  /// 生成数据指纹
  Future<String> _generateFingerprint(dynamic data) async {
    try {
      final jsonString = json.encode(data);
      final bytes = utf8.encode(jsonString);
      final digest = sha256.convert(bytes);
      return digest.toString();
    } catch (e) {
      print('Failed to generate fingerprint: $e');
      return '';
    }
  }
  
  /// 计算数据相似度
  Future<double> _calculateSimilarity(dynamic data1, dynamic data2) async {
    try {
      if (data1.runtimeType != data2.runtimeType) return 0.0;
      
      if (data1 is Map && data2 is Map) {
        // 计算Map类型数据的相似度
        final commonKeys = data1.keys.toSet().intersection(data2.keys.toSet());
        if (commonKeys.isEmpty) return 0.0;
        
        double similarity = 0.0;
        for (final key in commonKeys) {
          if (data1[key] == data2[key]) {
            similarity += 1.0;
          }
        }
        
        return similarity / max(data1.length, data2.length);
      }
      
      if (data1 is List && data2 is List) {
        // 计算List类型数据的相似度
        final commonLength = min(data1.length, data2.length);
        if (commonLength == 0) return 0.0;
        
        double similarity = 0.0;
        for (int i = 0; i < commonLength; i++) {
          if (data1[i] == data2[i]) {
            similarity += 1.0;
          }
        }
        
        return similarity / max(data1.length, data2.length);
      }
      
      // 简单类型数据的相似度
      return data1 == data2 ? 1.0 : 0.0;
    } catch (e) {
      print('Failed to calculate similarity: $e');
      return 0.0;
    }
  }
  
  /// 获取必填字段列表
  Set<String> _getRequiredFields(Map data) {
    // TODO: 根据数据类型返回相应的必填字段列表
    return {'id', 'timestamp', 'type'};
  }
  
  /// 计算最小值
  double min(num a, num b) => a < b ? a.toDouble() : b.toDouble();
  
  /// 计算最大值
  double max(num a, num b) => a > b ? a.toDouble() : b.toDouble();
}

/// 数据价值
class DataValue {
  final double score;
  final bool isValuable;
  final ValueMetrics metrics;
  final String fingerprint;
  
  DataValue({
    required this.score,
    required this.isValuable,
    required this.metrics,
    required this.fingerprint,
  });
  
  factory DataValue.empty() {
    return DataValue(
      score: 0.0,
      isValuable: false,
      metrics: ValueMetrics.empty(),
      fingerprint: '',
    );
  }
}

/// 价值度量指标
class ValueMetrics {
  final double freshness;
  final double completeness;
  final double correlation;
  final double frequency;
  
  ValueMetrics({
    required this.freshness,
    required this.completeness,
    required this.correlation,
    required this.frequency,
  });
  
  factory ValueMetrics.empty() {
    return ValueMetrics(
      freshness: 0.0,
      completeness: 0.0,
      correlation: 0.0,
      frequency: 0.0,
    );
  }
}

/// 数据上下文
class DataContext {
  final DateTime timestamp;
  final int accessCount;
  final List<dynamic> relatedData;
  
  DataContext({
    required this.timestamp,
    required this.accessCount,
    required this.relatedData,
  });
} 