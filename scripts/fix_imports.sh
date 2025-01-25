#!/bin/bash

# 修复 ui_components 引用
sed -i '' 's|libs/ui_components/styles/app_text_styles.dart|package:ui_components/styles/app_text_styles.dart|g' libs/core/lib/theme/app_theme.dart

# 移除 features_explore 引用
sed -i '' '/import.*features_explore.*coffee_time_page/d' libs/core/lib/router/app_router.dart

# 修复 core 服务引用
sed -i '' 's|core/lib/services/local_storage_service|../infrastructure/local_storage_service|g' libs/core/lib/services/notification_service_impl.dart

# 移除 suoke_score_lib 引用
sed -i '' '/import.*suoke_score_lib/d' libs/core/lib/services/infrastructure/redis_service_impl.dart

# 移除 llm_interaction_service_impl 引用
sed -i '' '/import.*llm_interaction_service_impl/d' libs/core/lib/di/injection.dart 