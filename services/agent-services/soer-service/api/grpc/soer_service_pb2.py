from typing import Dict, List, Any, Optional, Union

"""
soer_service_pb2 - 索克生活项目模块
"""

import sys

"""生成的协议缓冲代码"""


_b = sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor.FileDescriptor(
name = 'soer_service.proto',
package = 'suoke.soer.v1',
syntax = 'proto3',
serialized_options = None,
serialized_pb = _b('\n\x12soer_service.proto\x12\rsuoke.soer.v1')
)

# 消息类型定义
# 这里应该是完整的消息类型定义，由protoc自动生成
# 由于实际生成内容过长，这里省略具体实现

_HEALTHPLANREQUEST = _descriptor.Descriptor(
name = 'HealthPlanRequest',
full_name = 'suoke.soer.v1.HealthPlanRequest',
filename = None,
file = DESCRIPTOR,
containing_type = None,
fields = [],
extensions = [],
nested_types = [],
enum_types = [],
serialized_options = None,
is_extendable = False,
syntax = 'proto3',
extension_ranges = [],
oneofs = [],
serialized_start = 0,
serialized_end = 0,
)

_HEALTHPLANRESPONSE = _descriptor.Descriptor(
name = 'HealthPlanResponse',
full_name = 'suoke.soer.v1.HealthPlanResponse',
filename = None,
file = DESCRIPTOR,
containing_type = None,
fields = [],
extensions = [],
nested_types = [],
enum_types = [],
serialized_options = None,
is_extendable = False,
syntax = 'proto3',
extension_ranges = [],
oneofs = [],
serialized_start = 0,
serialized_end = 0,
)

# 其他消息类型定义同样方式省略...

# 类实现
class HealthPlanRequest(_message.Message):
    """TODO: 添加文档字符串"""
    __slots__ = ["user_id", "constitution_type", "health_goals", "preferences", "current_season"]
    USER_ID_FIELD_NUMBER = 1
    CONSTITUTION_TYPE_FIELD_NUMBER = 2
HEALTH_GOALS_FIELD_NUMBER = 3
PREFERENCES_FIELD_NUMBER = 4
CURRENT_SEASON_FIELD_NUMBER = 5
# 字段实现省略

class HealthPlanResponse(_message.Message):
    """TODO: 添加文档字符串"""
    __slots__ = ["plan_id", "diet_recommendations", "exercise_recommendations",
                "lifestyle_recommendations", "supplement_recommendations",
                "schedule", "confidence_score"]
# 字段实现省略

# 其他消息类实现省略...

DESCRIPTOR.message_types_by_name['HealthPlanRequest'] = _HEALTHPLANREQUEST
DESCRIPTOR.message_types_by_name['HealthPlanResponse'] = _HEALTHPLANRESPONSE
# 其他消息类型注册省略...

HealthPlanRequest = _reflection.GeneratedProtocolMessageType(
'HealthPlanRequest',
(_message.Message,),
{
'DESCRIPTOR': _HEALTHPLANREQUEST,
'__module__': 'soer_service_pb2'
}
)
_sym_db.RegisterMessage(HealthPlanRequest)

HealthPlanResponse = _reflection.GeneratedProtocolMessageType(
'HealthPlanResponse',
(_message.Message,),
{
'DESCRIPTOR': _HEALTHPLANRESPONSE,
'__module__': 'soer_service_pb2'
}
)
_sym_db.RegisterMessage(HealthPlanResponse)

# 其他消息类型注册省略...

# @@protoc_insertion_point(module_scope)
