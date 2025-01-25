#!/bin/bash

# 修复 redis 引用
sed -i '' 's|redis/commands|redis/redis|g' libs/core/lib/services/infrastructure/redis_service_impl.dart

# 修复 notification_service_impl 引用
sed -i '' 's|../infrastructure/local_storage_service|package:core/services/infrastructure/local_storage_service|g' libs/core/lib/services/notification_service_impl.dart

# 修复 app_theme.dart 的 riverpod 引用
sed -i '' 's|flutter_riverpod/flutter_riverpod|package:flutter_riverpod/flutter_riverpod|g' libs/core/lib/theme/app_theme.dart 