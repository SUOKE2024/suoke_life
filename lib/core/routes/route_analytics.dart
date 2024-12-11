import 'package:get/get.dart';
import '../logging/app_logger.dart';

class RouteAnalytics extends GetxService {
  static RouteAnalytics get to => Get.find();
  
  final _pageViews = <String, int>{}.obs;
  final _pageDurations = <String, Duration>{}.obs;
  final _pageTransitions = <String, Map<String, int>>{}.obs;
  
  // 记录页面访问
  void recordPageView(String routeName) {
    _pageViews[routeName] = (_pageViews[routeName] ?? 0) + 1;
    _logAnalytics('Page View', {'route': routeName, 'count': _pageViews[routeName]});
  }
  
  // 记录页面停留时间
  void recordPageDuration(String routeName, Duration duration) {
    final totalDuration = _pageDurations[routeName] ?? Duration.zero;
    _pageDurations[routeName] = totalDuration + duration;
    _logAnalytics('Page Duration', {
      'route': routeName,
      'duration': duration.inSeconds,
      'total': _pageDurations[routeName]?.inSeconds
    });
  }
  
  // 记录页面转换
  void recordTransition(String fromRoute, String toRoute) {
    final transitions = _pageTransitions[fromRoute] ?? {};
    transitions[toRoute] = (transitions[toRoute] ?? 0) + 1;
    _pageTransitions[fromRoute] = transitions;
    _logAnalytics('Page Transition', {
      'from': fromRoute,
      'to': toRoute,
      'count': transitions[toRoute]
    });
  }
  
  // 获取页面访问次数
  int getPageViews(String routeName) {
    return _pageViews[routeName] ?? 0;
  }
  
  // 获取页面平均停留时间
  Duration getAveragePageDuration(String routeName) {
    final totalDuration = _pageDurations[routeName] ?? Duration.zero;
    final views = _pageViews[routeName] ?? 1;
    return Duration(seconds: totalDuration.inSeconds ~/ views);
  }
  
  // 获取最常访问的页面
  List<MapEntry<String, int>> getMostVisitedPages({int limit = 10}) {
    final sorted = _pageViews.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return sorted.take(limit).toList();
  }
  
  // 获取页面转换频率
  Map<String, int> getPageTransitions(String fromRoute) {
    return Map.from(_pageTransitions[fromRoute] ?? {});
  }
  
  // 获取所有分析数据
  Map<String, dynamic> getAllAnalytics() {
    return {
      'pageViews': Map.from(_pageViews),
      'pageDurations': Map.from(_pageDurations),
      'pageTransitions': Map.from(_pageTransitions),
    };
  }
  
  // 清除分析数据
  void clearAnalytics() {
    _pageViews.clear();
    _pageDurations.clear();
    _pageTransitions.clear();
  }
  
  void _logAnalytics(String event, Map<String, dynamic> data) {
    AppLogger.instance.info(
      '$event: ${data.toString()}',
      tags: ['ANALYTICS'],
    );
  }
  
  // 导出分析报告
  String generateReport() {
    final buffer = StringBuffer();
    buffer.writeln('路由分析报告');
    buffer.writeln('生成时间: ${DateTime.now()}');
    buffer.writeln('\n访问次数最多的页面:');
    
    final mostVisited = getMostVisitedPages(limit: 5);
    for (final entry in mostVisited) {
      final avgDuration = getAveragePageDuration(entry.key);
      buffer.writeln(
        '${entry.key}: ${entry.value}次访问, 平均停留时间: ${avgDuration.inSeconds}秒',
      );
    }
    
    buffer.writeln('\n页面转换频率:');
    for (final fromRoute in _pageTransitions.keys) {
      buffer.writeln('从 $fromRoute 转换到:');
      final transitions = getPageTransitions(fromRoute);
      for (final toRoute in transitions.keys) {
        buffer.writeln('  $toRoute: ${transitions[toRoute]}次');
      }
    }
    
    return buffer.toString();
  }
} 