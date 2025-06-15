# 索克生活隐私合规机制设计与实现

## 1. 后端权限中间件

- 位置：`src/services/permission_middleware.py`
- 功能：基于用户角色的最小权限控制，防止越权访问。
- 用法：
  ```python
  from src.services.permission_middleware import PermissionMiddleware
  app.add_middleware(PermissionMiddleware)
  ```
- 说明：可扩展为RBAC/ABAC等更复杂权限模型。

---

## 2. 区块链零知识证明（ZKP）集成

- 位置：`src/services/zkp_utils.py`
- 功能：生成、验证健康数据零知识证明（ZKP），并支持上链存储。
- 用法：
  ```python
  from src.services.zkp_utils import generate_health_zkp, verify_health_zkp, store_zkp_on_chain
  proof = generate_health_zkp(user_id, health_data)
  if verify_health_zkp(proof):
      store_zkp_on_chain(proof)
  ```
- 说明：当前为伪代码接口，便于后续对接真实ZKP库和区块链SDK。

---

## 3. 合规报告自动推送

- 位置：`.github/workflows/ci-privacy.yml`
- 功能：CI合规检测失败时自动发送邮件通知合规负责人。
- 邮件内容：包含检测失败提醒和日志指引。
- 需配置SMTP服务器和密钥（见GitHub Secrets）。

---

## 4. 前后端调用与CI反馈

- 前端敏感信息展示、日志输出前统一调用 `src/utils/privacy.ts` 工具函数。
- 后端在 FastAPI 应用中添加 `PrivacyMaskingMiddleware` 和 `PermissionMiddleware`，所有API响应和权限自动保护。
- 区块链ZKP相关功能可通过 `zkp_utils.py` 及前端组件集成。
- CI自动运行 gitleaks、bandit、semgrep，发现问题自动阻断并推送报告。

---

## 5. 参考代码片段

### 权限中间件
```python
# 角色-权限映射
ROLE_PERMISSIONS = {
    "admin": [("GET", "/admin"), ("POST", "/admin")],
    "doctor": [("GET", "/patient"), ("POST", "/patient")],
    "user": [("GET", "/profile"), ("POST", "/health-data")],
}

def check_permission_rbac(user, path, method):
    if not user or "role" not in user:
        return False
    role = user["role"]
    allowed = ROLE_PERMISSIONS.get(role, [])
    # 支持模糊匹配
    return any(path.startswith(p) and method == m for m, p in allowed)

def check_permission_abac(user, path, method, attributes):
    # attributes: dict, 例如 {"department": "cardiology", "resource_owner": "user123"}
    if not user:
        return False
    # 例：只有本部门医生可访问本部门患者
    if user.get("role") == "doctor" and user.get("department") == attributes.get("department"):
        return True
    # 例：用户只能访问自己的数据
    if user.get("role") == "user" and user.get("user_id") == attributes.get("resource_owner"):
        return True
    return False
```

### ZKP生成与上链
```python
proof = generate_health_zkp(user_id, health_data)
if verify_health_zkp(proof):
    store_zkp_on_chain(proof)
```

### CI合规报告推送
```yaml
- name: 发送合规报告到邮箱
  if: failure()
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.suoke.com
    server_port: 465
    username: ${{ secrets.MAIL_USERNAME }}
    password: ${{ secrets.MAIL_PASSWORD }}
    subject: 索克生活隐私合规检测失败
    to: security@suoke.com
    from: ci-bot@suoke.com
    body: |
      CI合规检测失败，请及时处理。
      详情见GitHub Actions日志
```

---

## 6. 健康数据标准化（HL7/FHIR）

- 健康数据采集、存储、交换严格遵循国际/国内健康数据标准（如HL7、FHIR），便于后续扩展和与第三方系统对接。
- 已实现前后端FHIR Observation格式转换与校验工具，支持体温、血压等生命体征数据的标准化。
- 推荐所有健康数据接口、数据库存储、对外交换均采用FHIR标准格式。

### 后端示例（Python）
```python
from src.services.fhir_utils import to_fhir_observation_temperature, validate_fhir_observation
obs = to_fhir_observation_temperature("user123", 36.7, "Celsius", "2024-05-30T10:00:00+08:00")
assert validate_fhir_observation(obs)
```

### 前端示例（TypeScript）
```typescript
import { toFhirObservationTemperature, validateFhirObservation } from '../utils/fhir';
const obs = toFhirObservationTemperature('user123', 36.7, 'Celsius', '2024-05-30T10:00:00+08:00');
if (validateFhirObservation(obs)) {
  // 可安全用于存储、交换
}
```

---

## 7. 微服务边界清晰化与职责分离

- agent-services、diagnostic-services、integration-service等核心服务已进一步梳理边界，明确各自职责、接口和数据流，减少重复和耦合，提升可维护性和可扩展性。
- 所有服务接口均采用标准化（如FHIR、OpenAPI Schema），跨服务通信通过API/事件流解耦。
- 详细边界与接口梳理见 [docs/architecture/microservices_boundary.md](docs/architecture/microservices_boundary.md) 

### 真实ZKP库集成（如py-snark、zkproof等）
def generate_health_zkp_real(user_id: str, health_data: dict) -> dict:
    # TODO: 调用真实ZKP库生成proof
    # 例如：proof = zkproof.generate_proof(...)
    raise NotImplementedError("请集成真实ZKP库")

def verify_health_zkp_real(proof: dict) -> bool:
    # TODO: 调用真实ZKP库验证proof
    # 例如：zkproof.verify_proof(proof)
    raise NotImplementedError("请集成真实ZKP库")

# 区块链SDK集成（如web3.py、fabric-sdk-py等）
def store_zkp_on_chain_real(proof: dict):
    # TODO: 调用区块链SDK上链
    # 例如：web3.eth.sendTransaction(...)
    raise NotImplementedError("请集成区块链SDK") 

def to_fhir_observation_blood_pressure(user_id: str, systolic: float, diastolic: float, unit: str = "mmHg", effective_time: str = None):
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "85354-9", "display": "Blood pressure panel"}]},
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": effective_time,
        "component": [
            {
                "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic blood pressure"}]},
                "valueQuantity": {"value": systolic, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit}
            },
            {
                "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic blood pressure"}]},
                "valueQuantity": {"value": diastolic, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit}
            }
        ]
    }

def to_fhir_observation_heart_rate(user_id: str, value: float, unit: str = "bpm", effective_time: str = None):
    return {
        "resourceType": "Observation",
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]},
        "subject": {"reference": f"Patient/{user_id}"},
        "effectiveDateTime": effective_time,
        "valueQuantity": {"value": value, "unit": unit, "system": "http://unitsofmeasure.org", "code": unit},
    } 

---

## 8. 微服务边界最新优化

- agent-services 只负责智能体业务逻辑与编排，不直接处理底层诊断和数据采集。
- diagnostic-services 专注于诊断算法和健康指标分析，不与前端直接通信，仅暴露标准化API（如FHIR、OpenAPI Schema）。
- integration-service 只负责第三方系统对接、数据格式转换与合规校验，不实现业务决策。
- 所有健康数据、诊断结果等接口均推荐采用FHIR、OpenAPI Schema等标准格式。
- 跨服务通信推荐采用内存事件总线进一步解耦。
- 详细边界说明见 [docs/architecture/microservices_boundary.md](docs/architecture/microservices_boundary.md) 