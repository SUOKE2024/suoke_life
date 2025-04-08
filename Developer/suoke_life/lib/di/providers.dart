import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/domain/repositories/auth_repository.dart';

/// 主Provider导出文件
/// 按需导出各功能模块的Provider

// 核心服务提供者
export 'providers/core_providers.dart';

// 网络服务提供者
export 'providers/network_providers.dart';

// 数据存储提供者
export 'providers/storage_providers.dart';

// 数据感知提供者
export 'providers/sensing_providers.dart';

// 用户服务提供者
export 'providers/user_providers.dart';

// 路由提供者
export 'providers/router_providers.dart';

// AI服务提供者
export 'providers/ai_providers.dart';

// 健康服务提供者
export 'providers/health_providers.dart';

// TCM服务提供者
export 'providers/tcm_providers.dart';

// MCP服务提供者
export 'providers/mcp_providers.dart';

// 自动生成的Provider暂未实现
// export 'core/services/background_sensing_service.g.dart';
// export 'core/services/cloud_edge_collaboration_service.g.dart';
// export 'core/services/context_aware_sensing_service.g.dart';
// export 'core/services/edge_intelligence_service.g.dart';
// export 'core/services/multimodal_data_service.g.dart';
// export 'core/services/network_service.g.dart';
// export 'core/services/privacy_protection_service.g.dart';

// 导出传感器健康连接器服务
// export 'package:suoke_life/core/services/sensor_health_connector.dart';

// 数据同步提供者
export 'providers/sync_providers.dart';

// 导出所有Provider
export 'providers/api_providers.dart';
export 'providers/agent_providers.dart';
export 'providers/knowledge_providers.dart';
// 区块链提供者
export 'providers/blockchain_providers.dart';

/// 路由提供者
final appRouterProvider = Provider<AppRouter>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AppRouter(authGuard: AuthGuard(authRepository));
});
