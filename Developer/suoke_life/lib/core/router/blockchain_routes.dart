import 'package:auto_route/auto_route.dart';

/// 区块链模块路由配置
class BlockchainRoutes {
  // 定义区块链模块的路由
  static final List<AutoRoute> routes = [
    // 健康记录详情页面
    AutoRoute(
      path: '/blockchain/health-records/:recordId',
      page: HealthRecordDetailRoute.page,
    ),
    // 钱包页面
    AutoRoute(
      path: '/blockchain/wallet',
      page: WalletRoute.page,
    ),
    // 健康记录页面
    AutoRoute(
      path: '/blockchain/health-records',
      page: HealthRecordRoute.page,
    ),
  ];
}