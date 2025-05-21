# 区块链服务API文档

SoKe Life区块链服务提供了健康数据的区块链存储、验证和访问控制功能。本文档描述了该服务提供的gRPC接口。

## 服务定义

服务定义在`api/grpc/blockchain.proto`文件中，遵循Protocol Buffers和gRPC规范。

## 接口

### 存储健康数据

将健康数据存储到区块链上，确保数据的完整性和不可篡改性。

```protobuf
rpc StoreHealthData(StoreHealthDataRequest) returns (StoreHealthDataResponse);
```

#### 请求参数 (StoreHealthDataRequest)

| 字段           | 类型            | 描述                   |
|---------------|----------------|------------------------|
| user_id       | string         | 用户ID                  |
| data_type     | string         | 数据类型（如体重、血压等）  |
| data_hash     | bytes          | 数据哈希                 |
| encrypted_data| bytes          | 加密后的数据（可选）       |
| metadata      | map<string, string> | 元数据             |
| timestamp     | int64          | 时间戳                  |

#### 响应参数 (StoreHealthDataResponse)

| 字段           | 类型            | 描述                   |
|---------------|----------------|------------------------|
| transaction_id| string         | 区块链交易ID             |
| block_hash    | string         | 区块哈希                 |
| success       | bool           | 操作是否成功              |
| message       | string         | 操作结果消息              |

### 验证健康数据

验证链上存储的健康数据的完整性。

```protobuf
rpc VerifyHealthData(VerifyHealthDataRequest) returns (VerifyHealthDataResponse);
```

#### 请求参数 (VerifyHealthDataRequest)

| 字段           | 类型            | 描述                   |
|---------------|----------------|------------------------|
| transaction_id| string         | 交易ID                  |
| data_hash     | bytes          | 要验证的数据哈希           |

#### 响应参数 (VerifyHealthDataResponse)

| 字段                  | 类型            | 描述                   |
|----------------------|----------------|------------------------|
| valid                | bool           | 验证是否通过              |
| message              | string         | 验证结果消息              |
| verification_timestamp| int64         | 验证时间戳                |

### 零知识证明验证

使用零知识证明验证健康数据的特定属性，无需披露原始数据。

```protobuf
rpc VerifyWithZKP(VerifyWithZKPRequest) returns (VerifyWithZKPResponse);
```

#### 请求参数 (VerifyWithZKPRequest)

| 字段           | 类型            | 描述                   |
|---------------|----------------|------------------------|
| user_id       | string         | 用户ID                  |
| verifier_id   | string         | 验证者ID                 |
| data_type     | string         | 数据类型                 |
| proof         | bytes          | 零知识证明                |
| public_inputs | bytes          | 公共输入                 |

#### 响应参数 (VerifyWithZKPResponse)

| 字段                  | 类型                  | 描述                   |
|----------------------|----------------------|------------------------|
| valid                | bool                 | 验证是否通过              |
| message              | string               | 验证结果消息              |
| verification_details | map<string, string>  | 验证详情                 |

### 获取健康数据记录

获取用户的健康数据记录。

```protobuf
rpc GetHealthDataRecords(GetHealthDataRecordsRequest) returns (GetHealthDataRecordsResponse);
```

#### 请求参数 (GetHealthDataRecordsRequest)

| 字段           | 类型            | 描述                   |
|---------------|----------------|------------------------|
| user_id       | string         | 用户ID                  |
| data_type     | string         | 数据类型（可选）           |
| start_time    | int64          | 开始时间戳（可选）         |
| end_time      | int64          | 结束时间戳（可选）         |
| page          | int32          | 分页页码                 |
| page_size     | int32          | 每页大小                 |

#### 响应参数 (GetHealthDataRecordsResponse)

| 字段           | 类型                   | 描述                   |
|---------------|------------------------|------------------------|
| records       | repeated HealthDataRecord | 健康数据记录列表      |
| total_count   | int32                  | 总记录数                |
| page          | int32                  | 当前页码                |
| page_size     | int32                  | 每页大小                |

其中，HealthDataRecord定义如下：

| 字段           | 类型                   | 描述                   |
|---------------|------------------------|------------------------|
| transaction_id| string                 | 交易ID                 |
| data_type     | string                 | 数据类型                |
| data_hash     | bytes                  | 数据哈希                |
| metadata      | map<string, string>    | 元数据                  |
| timestamp     | int64                  | 时间戳                  |
| block_hash    | string                 | 区块哈希                |

### 授权访问健康数据

授权其他用户或服务访问健康数据。

```protobuf
rpc AuthorizeAccess(AuthorizeAccessRequest) returns (AuthorizeAccessResponse);
```

#### 请求参数 (AuthorizeAccessRequest)

| 字段              | 类型                   | 描述                   |
|------------------|------------------------|------------------------|
| user_id          | string                 | 数据所有者ID            |
| authorized_id    | string                 | 被授权方ID              |
| data_types       | repeated string        | 授权的数据类型列表       |
| expiration_time  | int64                  | 授权过期时间            |
| access_policies  | map<string, string>    | 访问策略                |

#### 响应参数 (AuthorizeAccessResponse)

| 字段              | 类型                   | 描述                   |
|------------------|------------------------|------------------------|
| authorization_id | string                 | 授权ID                 |
| success          | bool                   | 操作是否成功            |
| message          | string                 | 操作结果消息            |

### 撤销访问授权

撤销先前授予的健康数据访问权限。

```protobuf
rpc RevokeAccess(RevokeAccessRequest) returns (RevokeAccessResponse);
```

#### 请求参数 (RevokeAccessRequest)

| 字段              | 类型                   | 描述                   |
|------------------|------------------------|------------------------|
| authorization_id | string                 | 授权ID                 |
| user_id          | string                 | 数据所有者ID            |
| revocation_reason| string                 | 撤销原因（可选）         |

#### 响应参数 (RevokeAccessResponse)

| 字段                  | 类型                   | 描述                   |
|----------------------|------------------------|------------------------|
| success              | bool                   | 操作是否成功            |
| message              | string                 | 操作结果消息            |
| revocation_timestamp | int64                  | 撤销时间戳              |

### 获取区块链状态

获取区块链网络和节点的状态信息。

```protobuf
rpc GetBlockchainStatus(GetBlockchainStatusRequest) returns (GetBlockchainStatusResponse);
```

#### 请求参数 (GetBlockchainStatusRequest)

| 字段              | 类型                   | 描述                   |
|------------------|------------------------|------------------------|
| include_node_info| bool                   | 是否包含节点详细信息     |

#### 响应参数 (GetBlockchainStatusResponse)

| 字段                  | 类型                   | 描述                   |
|----------------------|------------------------|------------------------|
| current_block_height | int64                  | 当前区块高度            |
| connected_nodes      | int32                  | 已连接节点数量          |
| consensus_status     | string                 | 共识状态                |
| sync_percentage      | double                 | 同步百分比              |
| node_info            | map<string, string>    | 节点信息（如果请求）     |
| last_block_timestamp | int64                  | 最新区块时间戳          |

## 错误处理

服务使用标准的gRPC错误代码进行错误处理：

| 错误代码                | 描述                                        |
|------------------------|---------------------------------------------|
| INVALID_ARGUMENT       | 请求参数无效                                  |
| NOT_FOUND              | 请求的资源不存在                              |
| ALREADY_EXISTS         | 资源已存在                                    |
| PERMISSION_DENIED      | 权限不足                                      |
| UNAUTHENTICATED        | 未认证                                        |
| INTERNAL               | 服务器内部错误                                |
| UNAVAILABLE            | 服务不可用                                    |
| DEADLINE_EXCEEDED      | 请求超时                                      |

## 智能合约接口

区块链服务使用以下智能合约提供核心功能：

### HealthDataStorage 智能合约

负责健康数据的存储和验证。

主要功能：
- `storeHealthData` - 存储健康数据
- `verifyHealthData` - 验证健康数据完整性
- `getHealthDataRecord` - 获取健康数据记录
- `getUserDataTransactionIds` - 获取用户的所有健康数据记录ID

### ZKPVerifier 智能合约

负责零知识证明验证。

主要功能：
- `verifyProof` - 验证零知识证明
- `getVerificationRecord` - 获取验证记录
- `getUserVerifications` - 获取用户的所有验证记录

### AccessControl 智能合约

负责健康数据的访问控制。

主要功能：
- `grantAccess` - 授权访问
- `revokeAccess` - 撤销访问授权
- `checkAccess` - 检查访问权限
- `getAuthorization` - 获取授权详情

### SuoKeLifeContractFactory 智能合约

工厂合约，负责部署和管理所有智能合约。

主要功能：
- `deployContracts` - 部署所有合约
- `getContractAddresses` - 获取所有合约地址

## 数据类型

### 健康数据类型

区块链服务支持以下健康数据类型：

- `inquiry` - 问诊数据
- `listen` - 闻诊数据
- `look` - 望诊数据
- `palpation` - 切诊数据
- `vital_signs` - 生命体征
- `laboratory` - 实验室检查
- `medication` - 用药记录
- `nutrition` - 营养记录
- `activity` - 活动记录
- `sleep` - 睡眠记录
- `syndrome` - 证型记录
- `prescription` - 处方记录
- `health_plan` - 健康计划

### 访问级别

数据访问控制支持以下级别：

- `read` - 只读访问
- `write` - 读写访问
- `full` - 完全访问，包括删除

## 示例调用

### 存储健康数据示例

```python
# 创建健康数据存储请求
request = blockchain_pb2.StoreHealthDataRequest(
    user_id="user123",
    data_type="vital_signs",
    data_hash=b"0123456789abcdef0123456789abcdef",
    metadata={"source": "health_app", "device": "watch_v2"},
    timestamp=int(time.time())
)

# 调用gRPC方法
response = stub.StoreHealthData(request)

# 检查结果
if response.success:
    print(f"数据存储成功，交易ID: {response.transaction_id}")
else:
    print(f"数据存储失败: {response.message}")
```

### 授权访问示例

```python
# 创建授权请求
request = blockchain_pb2.AuthorizeAccessRequest(
    user_id="user123",
    authorized_id="doctor456",
    data_types=["vital_signs", "medication"],
    expiration_time=int((datetime.now() + timedelta(days=30)).timestamp()),
    access_policies={"read_only": "true", "purpose": "medical_diagnosis"}
)

# 调用gRPC方法
response = stub.AuthorizeAccess(request)

# 检查结果
if response.success:
    print(f"授权成功，授权ID: {response.authorization_id}")
else:
    print(f"授权失败: {response.message}")
``` 