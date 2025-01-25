#!/bin/bash

# 定义根目录
ROOT_DIR="."

# 创建 apps 目录
mkdir -p "$ROOT_DIR/apps"

# 定义 apps 目录下的服务
SERVICES=("ai_assistant_service" "health_service" "life_service" "user_service" "multimodal_service" "llm_service")

# 循环创建服务目录
for SERVICE in "${SERVICES[@]}"; do
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/data/datasources/local"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/data/datasources/remote"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/data/models"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/data/repositories"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/di"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/lib/services"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/test"
  mkdir -p "$ROOT_DIR/apps/$SERVICE/assets"
  touch "$ROOT_DIR/apps/$SERVICE/lib/di/register_module.dart"
  touch "$ROOT_DIR/apps/$SERVICE/lib/app.dart"
  touch "$ROOT_DIR/apps/$SERVICE/lib/main.dart"
  touch "$ROOT_DIR/apps/$SERVICE/Dockerfile"
  touch "$ROOT_DIR/apps/$SERVICE/pubspec.yaml"
  if [ "$SERVICE" == "ai_assistant_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/speech_service.dart"
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/llm_interaction_service.dart"
  elif [ "$SERVICE" == "health_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/health_advice_service.dart"
  elif [ "$SERVICE" == "life_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/life_record_service.dart"
  elif [ "$SERVICE" == "user_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/user_management_service.dart"
  elif [ "$SERVICE" == "multimodal_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/multimodal_processing_service.dart"
  elif [ "$SERVICE" == "llm_service" ]; then
    touch "$ROOT_DIR/apps/$SERVICE/lib/services/llm_service.dart"
  fi
done

# 创建 libs 目录
mkdir -p "$ROOT_DIR/libs/core/lib/config"
mkdir -p "$ROOT_DIR/libs/core/lib/database"
mkdir -p "$ROOT_DIR/libs/core/lib/di/modules"
mkdir -p "$ROOT_DIR/libs/core/lib/network"
mkdir -p "$ROOT_DIR/libs/core/lib/theme"
mkdir -p "$ROOT_DIR/libs/core/lib/utils"
mkdir -p "$ROOT_DIR/libs/core/lib/models"
mkdir -p "$ROOT_DIR/libs/core/lib/router"
mkdir -p "$ROOT_DIR/libs/core/lib/navigation"
mkdir -p "$ROOT_DIR/libs/core/lib/services"
touch "$ROOT_DIR/libs/core/lib/config/app_config.dart"
touch "$ROOT_DIR/libs/core/lib/database/database_config.dart"
touch "$ROOT_DIR/libs/core/lib/di/modules/storage_module.dart"
touch "$ROOT_DIR/libs/core/lib/di/modules/network_module.dart"
touch "$ROOT_DIR/libs/core/lib/network/health_service_client.dart"
touch "$ROOT_DIR/libs/core/lib/network/life_service_client.dart"
touch "$ROOT_DIR/libs/core/lib/network/llm_service_client.dart"
touch "$ROOT_DIR/libs/core/lib/network/multimodal_service_client.dart"
touch "$ROOT_DIR/libs/core/lib/network/user_service_client.dart"
touch "$ROOT_DIR/libs/core/lib/theme/app_theme.dart"
touch "$ROOT_DIR/libs/core/lib/utils/error_handler.dart"
touch "$ROOT_DIR/libs/core/lib/router/app_router.dart"
touch "$ROOT_DIR/libs/core/lib/navigation/app_routes.dart"
touch "$ROOT_DIR/libs/core/lib/services/local_storage_service.dart"

# 创建 features 目录
mkdir -p "$ROOT_DIR/features"
FEATURES=("home" "suoke" "explore" "life" "profile")
for FEATURE in "${FEATURES[@]}"; do
  mkdir -p "$ROOT_DIR/features/$FEATURE/lib/models"
  mkdir -p "$ROOT_DIR/features/$FEATURE/lib/pages"
  mkdir -p "$ROOT_DIR/features/$FEATURE/lib/providers"
  mkdir -p "$ROOT_DIR/features/$FEATURE/lib/services"
  mkdir -p "$ROOT_DIR/features/$FEATURE/lib/widgets"
  mkdir -p "$ROOT_DIR/features/$FEATURE/test"
  mkdir -p "$ROOT_DIR/features/$FEATURE/assets"
  if [ "$FEATURE" == "home" ]; then
    touch "$ROOT_DIR/features/$FEATURE/lib/pages/chat_page.dart"
  fi
done

# 创建 scripts 目录
mkdir -p "$ROOT_DIR/scripts"

# 创建 tests 目录
mkdir -p "$ROOT_DIR/test/features/home/pages"
mkdir -p "$ROOT_DIR/test/core/services"
touch "$ROOT_DIR/test/core/models/user_test.dart"
touch "$ROOT_DIR/test/core/models/settings_test.dart"
touch "$ROOT_DIR/test/core/models/life_record_test.dart"
touch "$ROOT_DIR/test/core/services/ai_service_test.dart"
touch "$ROOT_DIR/test/core/services/chat_service_test.dart"
touch "$ROOT_DIR/test/core/services/expert_service_test.dart"
touch "$ROOT_DIR/test/core/services/health_service_test.dart"
touch "$ROOT_DIR/test/core/services/payment_service_test.dart"
touch "$ROOT_DIR/test/core/services/notification_service_test.dart"
touch "$ROOT_DIR/test/core/services/analytics_service_test.dart"
touch "$ROOT_DIR/test/core/services/data_sync_service_test.dart"
touch "$ROOT_DIR/test/features/home/pages/chat_page_test.dart"

echo "APP 目录结构创建完成" 