#!/bin/bash

# 要删除的文件列表
files_to_remove=(
  "lib/app/presentation/pages/chat/chat_page.dart"
  "lib/app/presentation/pages/explore/search_page.dart"
  "lib/app/presentation/pages/life/user_profile_page.dart"
  "lib/app/presentation/pages/base/base_page.dart"
  "lib/app/presentation/pages/empty/empty_page.dart"
  "lib/app/presentation/pages/error/error_page.dart"
  "lib/app/presentation/pages/loading/loading_page.dart"
  "lib/app/presentation/pages/auth/register_controller.dart"
  "lib/app/presentation/pages/auth/login_controller.dart"
  "lib/app/presentation/pages/home/home_controller.dart"
  "lib/app/presentation/pages/auth/forgot_password_page.dart"
  "lib/app/presentation/pages/auth/register_page.dart"
  "lib/app/presentation/pages/explore/food_page.dart"
  "lib/app/presentation/pages/explore/flower_page.dart"
  "lib/app/presentation/pages/explore/mushroom_page.dart"
  "lib/app/presentation/pages/explore/accommodation_page.dart"
  "lib/app/presentation/pages/explore/hotspot_page.dart"
  "lib/app/presentation/pages/explore/treasure_hunt_page.dart"
  "lib/app/presentation/pages/suoke/vital_signs_page.dart"
  "lib/app/presentation/pages/suoke/api_services_page.dart"
  "lib/app/presentation/pages/suoke/supply_chain_page.dart"
  "lib/app/presentation/pages/life/points_page.dart"
  "lib/app/presentation/pages/life/rewards_page.dart"
  "lib/app/presentation/pages/profile/history_page.dart"
  "lib/app/presentation/pages/profile/favorites_page.dart"
  "lib/app/presentation/pages/profile/help_page.dart"
  "lib/app/presentation/pages/profile/feedback_page.dart"
  "lib/app/presentation/pages/profile/user_agreement_page.dart"
  "lib/app/presentation/pages/profile/privacy_policy_page.dart"
  "lib/app/presentation/pages/profile/licenses_page.dart"
)

# 删除文件
for file in "${files_to_remove[@]}"; do
  if [ -f "$file" ]; then
    rm "$file"
    echo "Deleted: $file"
  else
    echo "Not found: $file"
  fi
done

# 删除空目录
find lib/app/presentation/pages -type d -empty -delete 