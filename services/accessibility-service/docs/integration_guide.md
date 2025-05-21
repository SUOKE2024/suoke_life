# 索克生活无障碍服务集成指南

本指南详细介绍如何将索克生活无障碍服务与四大智能体（小艾、小克、老克、索儿）进行集成，包括API调用、事件通知和功能注册等关键流程。

## 目录

- [服务概述](#服务概述)
- [集成准备](#集成准备)
- [与小艾(xiaoai)集成](#与小艾xiaoai集成)
- [与小克(xiaoke)集成](#与小克xiaoke集成)
- [与老克(laoke)集成](#与老克laoke集成)
- [与索儿(soer)集成](#与索儿soer集成)
- [后台数据收集集成](#后台数据收集集成)
- [危机报警服务集成](#危机报警服务集成)
- [安全与隐私](#安全与隐私)
- [故障排除](#故障排除)

## 服务概述

索克生活无障碍服务提供全面的无障碍功能支持，包括：

- **导盲服务**：场景识别和障碍物检测
- **手语识别**：将手语视频转换为文本
- **屏幕阅读**：提供屏幕内容的语音描述
- **语音辅助**：支持27种方言的语音交互
- **健康内容无障碍转换**：将健康内容转换为无障碍格式
- **无障碍设置管理**：统一的用户无障碍设置管理
- **后台数据采集服务**：在设备待机和息屏条件下持续采集健康数据
- **危机报警服务**：分析用户健康数据，检测异常并触发多级报警

## 集成准备

### 获取访问凭证

集成前，需要向无障碍服务团队申请服务访问凭证：

```bash
curl -X POST "https://auth.suoke.life/services/accessibility/credentials" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "xiaoai", 
    "description": "小艾智能体与无障碍服务集成", 
    "contact_email": "xiaoai-team@suoke.life"
  }'
```

成功后，您将收到服务ID和密钥：

```json
{
  "service_id": "svc_accessibility_xiaoai_001",
  "service_key": "sk_acc_7f4d2b1a8e9c5f3d6..."
}
```

### 服务发现

通过服务发现获取无障碍服务端点：

```python
import requests

def discover_accessibility_service():
    response = requests.get(
        "https://discovery.suoke.life/services/accessibility",
        headers={"Authorization": f"Bearer {YOUR_SERVICE_KEY}"}
    )
    return response.json()
```

## 与小艾(xiaoai)集成

### 导盲服务集成

小艾智能体主要通过导盲服务协助视障用户理解环境：

```python
import grpc
from suoke.accessibility.v1 import accessibility_pb2, accessibility_pb2_grpc

def xiaoai_blind_assistance_integration(image_data, user_id, preferences, location):
    # 创建gRPC通道并初始化客户端
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 构造请求
    request = accessibility_pb2.BlindAssistanceRequest(
        image_data=image_data,
        user_id=user_id,
        preferences=preferences,
        location=location
    )
    
    # 调用服务
    response = client.BlindAssistance(request)
    
    # 处理响应
    return {
        "scene_description": response.scene_description,
        "obstacles": [
            {
                "type": obstacle.type,
                "distance": obstacle.distance,
                "direction": obstacle.direction
            } for obstacle in response.obstacles
        ],
        "navigation_guidance": response.navigation_guidance,
        "audio_guidance": response.audio_guidance
    }
```

### 手语识别集成

小艾需要手语识别功能与听障用户交流：

```python
def xiaoai_sign_language_integration(video_data, user_id, language="zh-CN"):
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    request = accessibility_pb2.SignLanguageRequest(
        video_data=video_data,
        user_id=user_id,
        language=language
    )
    
    response = client.SignLanguageRecognition(request)
    
    return {
        "text": response.text,
        "confidence": response.confidence,
        "segments": [
            {
                "text": seg.text,
                "start_time": seg.start_time_ms,
                "end_time": seg.end_time_ms
            } for seg in response.segments
        ]
    }
```

## 与小克(xiaoke)集成

### 医疗资源无障碍服务

小克智能体负责医疗资源调度，需要确保预约流程对所有用户友好：

```python
def xiaoke_medical_resource_accessibility(user_id, content_id, content_type):
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 获取用户无障碍设置
    settings_request = accessibility_pb2.SettingsRequest(
        user_id=user_id,
        action="GET"
    )
    settings_response = client.ManageSettings(settings_request)
    
    # 转换医疗内容为无障碍格式
    content_request = accessibility_pb2.AccessibleContentRequest(
        content_id=content_id,
        content_type=content_type,
        user_id=user_id,
        target_format="AUTO",
        preferences=settings_response.current_preferences
    )
    
    content_response = client.AccessibleContent(content_request)
    
    return {
        "accessible_content": content_response.accessible_content,
        "content_url": content_response.content_url,
        "audio_content": content_response.audio_content
    }
```

## 与老克(laoke)集成

### 知识内容无障碍转换

老克智能体使用无障碍服务转换中医知识内容：

```python
def laoke_knowledge_accessibility(content_id, user_id, target_format="ALL"):
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 获取用户无障碍设置
    settings_request = accessibility_pb2.SettingsRequest(
        user_id=user_id,
        action="GET"
    )
    settings_response = client.ManageSettings(settings_request)
    
    # 转换知识内容为无障碍格式
    content_request = accessibility_pb2.AccessibleContentRequest(
        content_id=content_id,
        content_type="KNOWLEDGE",
        user_id=user_id,
        target_format=target_format,
        preferences=settings_response.current_preferences
    )
    
    content_response = client.AccessibleContent(content_request)
    
    # 返回转换结果
    result = {
        "text": content_response.accessible_content,
        "urls": {}
    }
    
    if content_response.content_url:
        result["urls"]["web"] = content_response.content_url
    
    if content_response.audio_content:
        # 保存音频并返回URL
        audio_path = f"/content/audio/{content_id}.mp3"
        with open(audio_path, "wb") as f:
            f.write(content_response.audio_content)
        result["urls"]["audio"] = f"https://cdn.suoke.life/content/audio/{content_id}.mp3"
    
    if content_response.tactile_content:
        # 保存盲文内容并返回URL
        tactile_path = f"/content/tactile/{content_id}.brf"
        with open(tactile_path, "wb") as f:
            f.write(content_response.tactile_content)
        result["urls"]["tactile"] = f"https://cdn.suoke.life/content/tactile/{content_id}.brf"
    
    return result
```

## 与索儿(soer)集成

### 生活管理无障碍支持

索儿智能体使用无障碍服务支持用户进行健康数据理解和决策：

```python
def soer_health_data_accessibility(health_data, user_id):
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 获取用户无障碍设置
    settings_request = accessibility_pb2.SettingsRequest(
        user_id=user_id,
        action="GET"
    )
    settings_response = client.ManageSettings(settings_request)
    
    # 创建无障碍健康内容
    content_request = accessibility_pb2.AccessibleContentRequest(
        content_id=f"health_data_{int(time.time())}",
        content_type="HEALTH_DATA",
        user_id=user_id,
        target_format="ALL",
        preferences=settings_response.current_preferences
    )
    
    # 将健康数据转换为无障碍格式
    content_response = client.AccessibleContent(content_request)
    
    return {
        "accessible_description": content_response.accessible_content,
        "audio_description": content_response.audio_content
    }
```

## 后台数据收集集成

### 配置数据收集

配置用户设备的后台健康数据收集功能：

```python
def configure_background_collection(user_id, device_info, data_types=None):
    """
    配置后台数据收集服务
    
    Args:
        user_id: 用户ID
        device_info: 设备信息
        data_types: 要收集的数据类型列表，如不提供则使用默认设置
        
    Returns:
        配置结果
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 默认数据类型
    if data_types is None:
        data_types = ["pulse", "sleep", "activity", "environment", "voice"]
    
    # 创建设备信息
    device_info_msg = accessibility_pb2.DeviceInfo(
        device_id=device_info.get("device_id", ""),
        device_model=device_info.get("device_model", ""),
        os_version=device_info.get("os_version", ""),
        app_version=device_info.get("app_version", ""),
        sdk_version=device_info.get("sdk_version", "")
    )
    
    # 创建默认配置
    config = accessibility_pb2.CollectionConfiguration(
        collection_interval_seconds=300,  # 5分钟
        upload_interval_seconds=3600,    # 1小时
        battery_optimization=True,
        low_battery_threshold=20,
        collect_during_sleep=True,
        storage_policy="ENCRYPT_AND_COMPRESS",
        data_retention_days=30,
        encrypt_data=True
    )
    
    # 构造请求
    request = accessibility_pb2.BackgroundCollectionRequest(
        user_id=user_id,
        configuration=config,
        data_types=data_types,
        device_info=device_info_msg
    )
    
    # 调用服务
    response = client.ConfigureBackgroundCollection(request)
    
    return {
        "success": response.success,
        "message": response.message,
        "collection_id": response.collection_id,
        "config": {
            "collection_interval": response.applied_configuration.collection_interval_seconds,
            "upload_interval": response.applied_configuration.upload_interval_seconds,
            "battery_optimization": response.applied_configuration.battery_optimization,
            "low_battery_threshold": response.applied_configuration.low_battery_threshold
        }
    }
```

### 提交收集的数据

将设备收集的健康数据提交到服务器：

```python
def submit_collected_data(user_id, device_id, collection_id, data_points, device_info):
    """
    提交收集的健康数据
    
    Args:
        user_id: 用户ID
        device_id: 设备ID
        collection_id: 收集ID
        data_points: 健康数据点列表
        device_info: 设备信息
        
    Returns:
        提交结果
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 创建设备信息
    device_info_msg = accessibility_pb2.DeviceInfo(
        device_id=device_info.get("device_id", ""),
        device_model=device_info.get("device_model", ""),
        os_version=device_info.get("os_version", ""),
        app_version=device_info.get("app_version", ""),
        sdk_version=device_info.get("sdk_version", "")
    )
    
    # 创建数据点
    data_points_msg = []
    for point in data_points:
        # 创建元数据字典
        metadata = point.get("metadata", {})
        
        health_point = accessibility_pb2.HealthDataPoint(
            data_type=point.get("data_type", ""),
            value=point.get("value", ""),
            timestamp=point.get("timestamp", int(time.time())),
            confidence=point.get("confidence", 1.0),
            metadata=metadata,
            binary_data=point.get("binary_data", b"")
        )
        data_points_msg.append(health_point)
    
    # 构造请求
    request = accessibility_pb2.CollectedDataRequest(
        user_id=user_id,
        device_id=device_id,
        collection_id=collection_id,
        data_points=data_points_msg,
        device_info=device_info_msg,
        batch_id=f"batch_{int(time.time())}",
        timestamp=int(time.time())
    )
    
    # 调用服务
    response = client.SubmitCollectedData(request)
    
    result = {
        "success": response.success,
        "message": response.message,
        "accepted_points": response.accepted_points,
        "rejected_points": response.rejected_points
    }
    
    # 如果触发了警报，则通知智能体
    if response.alerts:
        result["alerts"] = response.alerts
        notify_agents_about_alerts(user_id, response.alerts)
    
    return result
```

### 获取收集状态

查询当前数据收集服务的状态：

```python
def get_collection_status(user_id, device_id):
    """
    获取后台数据收集状态
    
    Args:
        user_id: 用户ID
        device_id: 设备ID
        
    Returns:
        收集状态信息
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 构造请求
    request = accessibility_pb2.CollectionStatusRequest(
        user_id=user_id,
        device_id=device_id
    )
    
    # 调用服务
    response = client.GetCollectionStatus(request)
    
    # 处理数据类型状态
    data_types = []
    for dt in response.data_types:
        data_types.append({
            "data_type": dt.data_type,
            "is_collecting": dt.is_collecting,
            "collection_frequency": dt.collection_frequency,
            "last_collection_time": dt.last_collection_time
        })
    
    # 返回状态信息
    return {
        "is_active": response.is_active,
        "configuration": {
            "collection_interval": response.current_configuration.collection_interval_seconds,
            "upload_interval": response.current_configuration.upload_interval_seconds,
            "battery_optimization": response.current_configuration.battery_optimization
        },
        "last_collection_time": response.last_collection_time,
        "last_upload_time": response.last_upload_time,
        "stored_data_size": response.stored_data_bytes,
        "data_types": data_types,
        "battery_status": {
            "level": response.battery_status.level,
            "is_charging": response.battery_status.is_charging,
            "power_mode": response.battery_status.power_mode
        },
        "user_state": {
            "state": response.user_state.state,
            "duration": response.user_state.state_duration_seconds,
            "confidence": response.user_state.confidence
        }
    }
```

## 危机报警服务集成

### 触发健康警报

当检测到潜在健康问题时，手动触发健康警报：

```python
def trigger_health_alert(user_id, device_id, alert_level, alert_type, description, data_points=None, context=None):
    """
    触发健康警报
    
    Args:
        user_id: 用户ID
        device_id: 设备ID
        alert_level: 警报级别 (INFORMATION, WARNING, DANGER, CRITICAL)
        alert_type: 警报类型
        description: 警报描述
        data_points: 相关健康数据点
        context: 上下文信息
        
    Returns:
        警报触发结果
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 创建数据点列表
    data_points_msg = []
    if data_points:
        for point in data_points:
            health_point = accessibility_pb2.HealthDataPoint(
                data_type=point.get("data_type", ""),
                value=point.get("value", ""),
                timestamp=point.get("timestamp", int(time.time())),
                confidence=point.get("confidence", 1.0),
                metadata=point.get("metadata", {}),
                binary_data=point.get("binary_data", b"")
            )
            data_points_msg.append(health_point)
    
    # 创建警报级别枚举
    alert_level_enum = accessibility_pb2.AlertLevel.INFORMATION
    if alert_level == "WARNING":
        alert_level_enum = accessibility_pb2.AlertLevel.WARNING
    elif alert_level == "DANGER":
        alert_level_enum = accessibility_pb2.AlertLevel.DANGER
    elif alert_level == "CRITICAL":
        alert_level_enum = accessibility_pb2.AlertLevel.CRITICAL
    
    # 构造请求
    request = accessibility_pb2.HealthAlertRequest(
        user_id=user_id,
        device_id=device_id,
        alert_level=alert_level_enum,
        alert_type=alert_type,
        description=description,
        data_points=data_points_msg,
        context=context or {},
        timestamp=int(time.time()),
        require_acknowledgment=alert_level_enum >= accessibility_pb2.AlertLevel.WARNING
    )
    
    # 调用服务
    response = client.TriggerHealthAlert(request)
    
    # 处理智能体行动
    agent_actions = []
    for action in response.agent_actions:
        agent_actions.append({
            "agent_id": action.agent_id,
            "action_type": action.action_type,
            "description": action.description,
            "timestamp": action.timestamp
        })
    
    # 处理推荐行动
    recommended_action = None
    if response.recommended_action:
        recommended_action = {
            "action_type": response.recommended_action.action_type,
            "description": response.recommended_action.description,
            "urgency_level": response.recommended_action.urgency_level,
            "instruction": response.recommended_action.instruction
        }
    
    return {
        "success": response.success,
        "alert_id": response.alert_id,
        "message": response.message,
        "notified_contacts": response.notified_contacts,
        "agent_actions": agent_actions,
        "recommended_action": recommended_action
    }
```

### 配置警报阈值

为用户配置个性化的健康警报阈值：

```python
def configure_alert_thresholds(user_id, thresholds):
    """
    配置健康警报阈值
    
    Args:
        user_id: 用户ID
        thresholds: 阈值设置列表
        
    Returns:
        配置结果
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 创建阈值消息列表
    thresholds_msg = []
    for t in thresholds:
        # 创建阈值方向枚举
        direction = accessibility_pb2.ThresholdDirection.ABOVE
        if t.get("direction") == "BELOW":
            direction = accessibility_pb2.ThresholdDirection.BELOW
        elif t.get("direction") == "EQUAL":
            direction = accessibility_pb2.ThresholdDirection.EQUAL
        elif t.get("direction") == "CHANGE_RATE":
            direction = accessibility_pb2.ThresholdDirection.CHANGE_RATE
        
        threshold = accessibility_pb2.AlertThreshold(
            data_type=t.get("data_type", ""),
            warning_threshold=t.get("warning_threshold", 0.0),
            danger_threshold=t.get("danger_threshold", 0.0),
            critical_threshold=t.get("critical_threshold", 0.0),
            direction=direction,
            sustained_seconds=t.get("sustained_seconds", 0)
        )
        thresholds_msg.append(threshold)
    
    # 构造请求
    request = accessibility_pb2.AlertThresholdsRequest(
        user_id=user_id,
        thresholds=thresholds_msg
    )
    
    # 调用服务
    response = client.ConfigureAlertThresholds(request)
    
    # 处理应用的阈值
    applied_thresholds = []
    for t in response.applied_thresholds:
        direction_str = "ABOVE"
        if t.direction == accessibility_pb2.ThresholdDirection.BELOW:
            direction_str = "BELOW"
        elif t.direction == accessibility_pb2.ThresholdDirection.EQUAL:
            direction_str = "EQUAL"
        elif t.direction == accessibility_pb2.ThresholdDirection.CHANGE_RATE:
            direction_str = "CHANGE_RATE"
            
        applied_thresholds.append({
            "data_type": t.data_type,
            "warning_threshold": t.warning_threshold,
            "danger_threshold": t.danger_threshold,
            "critical_threshold": t.critical_threshold,
            "direction": direction_str,
            "sustained_seconds": t.sustained_seconds
        })
    
    return {
        "success": response.success,
        "message": response.message,
        "applied_thresholds": applied_thresholds
    }
```

### 获取警报历史

查询用户的健康警报历史：

```python
def get_alert_history(user_id, start_time=None, end_time=None, alert_type=None, min_level="INFORMATION", max_results=20):
    """
    获取健康警报历史
    
    Args:
        user_id: 用户ID
        start_time: 开始时间（时间戳）
        end_time: 结束时间（时间戳）
        alert_type: 警报类型
        min_level: 最低警报级别
        max_results: 最大结果数
        
    Returns:
        警报历史记录
    """
    channel = grpc.secure_channel(
        "accessibility.suoke.life:443",
        grpc.ssl_channel_credentials()
    )
    client = accessibility_pb2_grpc.AccessibilityServiceStub(channel)
    
    # 设置默认时间
    if start_time is None:
        # 默认查询最近7天的警报
        start_time = int(time.time()) - (7 * 24 * 60 * 60)
    
    if end_time is None:
        end_time = int(time.time())
    
    # 创建警报级别枚举
    min_level_enum = accessibility_pb2.AlertLevel.INFORMATION
    if min_level == "WARNING":
        min_level_enum = accessibility_pb2.AlertLevel.WARNING
    elif min_level == "DANGER":
        min_level_enum = accessibility_pb2.AlertLevel.DANGER
    elif min_level == "CRITICAL":
        min_level_enum = accessibility_pb2.AlertLevel.CRITICAL
    
    # 构造请求
    request = accessibility_pb2.AlertHistoryRequest(
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        alert_type=alert_type or "",
        min_level=min_level_enum,
        max_results=max_results
    )
    
    # 调用服务
    response = client.GetAlertHistory(request)
    
    # 处理警报记录
    alerts = []
    for alert in response.alerts:
        # 处理警报级别
        level_str = "INFORMATION"
        if alert.alert_level == accessibility_pb2.AlertLevel.WARNING:
            level_str = "WARNING"
        elif alert.alert_level == accessibility_pb2.AlertLevel.DANGER:
            level_str = "DANGER"
        elif alert.alert_level == accessibility_pb2.AlertLevel.CRITICAL:
            level_str = "CRITICAL"
        
        # 处理智能体行动
        agent_actions = []
        for action in alert.agent_actions:
            agent_actions.append({
                "agent_id": action.agent_id,
                "action_type": action.action_type,
                "description": action.description,
                "timestamp": action.timestamp
            })
        
        alerts.append({
            "alert_id": alert.alert_id,
            "user_id": alert.user_id,
            "alert_level": level_str,
            "alert_type": alert.alert_type,
            "description": alert.description,
            "timestamp": alert.timestamp,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
            "notified_contacts": alert.notified_contacts,
            "agent_actions": agent_actions
        })
    
    return {
        "success": response.success,
        "message": response.message,
        "alerts": alerts,
        "has_more": response.has_more,
        "total_count": response.total_count
    }
```

## 安全与隐私

无障碍服务严格遵守隐私保护原则，特别是在处理健康数据时。集成者应当：

1. **加密所有传输中的敏感数据**，包括用户身份信息和健康数据。
2. **获取明确用户同意**，尤其是对特殊类型数据（如语音、视频）的收集。
3. **实施数据最小化原则**，仅收集完成功能所必需的数据。
4. **合理设置数据保留政策**，不保留超过必要期限的数据。
5. **提供数据导出和删除机制**，满足数据主体请求的能力。

API调用示例：

```python
def update_user_privacy_settings(user_id, settings):
    """更新用户隐私设置"""
    # 实现隐私设置更新逻辑
    pass
```

## 故障排除

### 常见问题

1. **gRPC连接错误**
   - 检查网络连接
   - 验证服务凭证是否有效
   - 检查服务端点是否正确

2. **认证失败**
   - 确认服务ID和密钥正确
   - 检查凭证是否过期
   - 联系无障碍服务团队重置凭证

3. **响应超时**
   - 检查请求数据大小，考虑分批处理
   - 检查网络延迟情况
   - 实现适当的重试机制

### 联系支持

技术支持邮箱：accessibility-team@suoke.life

API文档：https://docs.suoke.life/accessibility-service/api 