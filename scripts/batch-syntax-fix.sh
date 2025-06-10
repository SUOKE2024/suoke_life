#!/bin/bash

# 索克生活项目批量语法修复脚本
# 修复发现的所有语法错误

echo "🔧 开始批量修复语法错误..."

# 修复 useAgent.tsx 中的语法错误
echo "修复 useAgent.tsx..."
sed -i '' 's/selectedAgent: AgentType;,/selectedAgent: AgentType;/g' src/hooks/useAgent.tsx
sed -i '' 's/setSelectedAgent: (agent: AgentType) => void;,/setSelectedAgent: (agent: AgentType) => void;/g' src/hooks/useAgent.tsx
sed -i '' 's/switchAgent: (agent: AgentType) => void;,/switchAgent: (agent: AgentType) => void;/g' src/hooks/useAgent.tsx
sed -i '' 's/getAgentInfo: (agent: AgentType) => any;,/getAgentInfo: (agent: AgentType) => any;/g' src/hooks/useAgent.tsx

# 修复 privacy.ts 中的语法错误
echo "修复 privacy.ts..."
sed -i '' 's/sanitizeLogData;/sanitizeLogData,/g' src/utils/privacy.ts

# 修复 TCM.d.test.ts 中的导入错误
echo "修复 TCM.d.test.ts..."
sed -i '' 's/import TCM.d from/import * as TCM from/g' src/types/__tests__/TCM.d.test.ts
sed -i '' 's/expect(TCM.d)/expect(TCM)/g' src/types/__tests__/TCM.d.test.ts

# 修复 multimodal/index.ts 中的语法错误
echo "修复 multimodal/index.ts..."
sed -i '' 's/} as MultimodalQuery, \*\/\/\/$/} as MultimodalQuery;/g' src/core/multimodal/index.ts
sed -i '' '/^\*\/\/\/$/d' src/core/multimodal/index.ts

# 修复 onnx-runtime/index.ts 中的导入错误
echo "修复 onnx-runtime/index.ts..."
sed -i '' 's/from "\.\/    /from "\.\//g' src/core/onnx-runtime/index.ts
sed -i '' 's/from "\.\.\/\.\.\/placeholder"\.\/    /from "\.\.\/\.\.\/placeholder"\./g' src/core/onnx-runtime/index.ts

# 修复 chat.ts 中的语法错误
echo "修复 chat.ts..."
sed -i '' 's/id: string}/id: string;/g' src/types/chat.ts
sed -i '' 's/name: string,/name: string;/g' src/types/chat.ts
sed -i '' 's/type: ChannelType,/type: ChannelType;/g' src/types/chat.ts
sed -i '' 's/avatar: string,/avatar: string;/g' src/types/chat.ts

# 修复 onnx-runtime/types.ts 中的语法错误
echo "修复 onnx-runtime/types.ts..."
sed -i '' 's/float32" | int32" | "uint8 | "int64" | bool";/export type DataType = "float32" | "int32" | "uint8" | "int64" | "bool";/g' src/core/onnx-runtime/types.ts

# 修复 maze.ts 中的语法错误
echo "修复 maze.ts..."
sed -i '' 's/x: number;,/x: number;/g' src/types/maze.ts

# 修复 fhir.ts 中的语法错误
echo "修复 fhir.ts..."
sed -i '' 's/resourceType: "Observation";,/resourceType: "Observation";/g' src/utils/fhir.ts
sed -i '' 's/status: string;,/status: string;/g' src/utils/fhir.ts
sed -i '' 's/category: Array<{;,/category: Array<{/g' src/utils/fhir.ts
sed -i '' 's/coding: Array<{;,/coding: Array<{/g' src/utils/fhir.ts

echo "✅ 批量语法修复完成！" 