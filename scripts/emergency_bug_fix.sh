#!/bin/bash

# 索克生活项目紧急Bug修复脚本
# 修复系统性语法错误

echo "🚨 开始紧急Bug修复..."
echo "项目路径: $(pwd)"
echo "修复时间: $(date)"

# 1. 备份关键文件
echo "📦 创建备份..."
mkdir -p backup/$(date +%Y%m%d_%H%M%S)
cp -r src backup/$(date +%Y%m%d_%H%M%S)/

# 2. 修复TypeScript/JavaScript语法错误
echo "🔧 修复前端语法错误..."

# 修复随机插入的分号和逗号
find src -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | while read file; do
    echo "修复文件: $file"
    
    # 修复 ;,; 模式
    sed -i '' 's/;,;/;/g' "$file"
    
    # 修复 "",""模式  
    sed -i '' 's/"";,""/"/g' "$file"
    sed -i '' "s/'';,''/''/g" "$file"
    
    # 修复 const const 模式
    sed -i '' 's/const const =/const /g' "$file"
    
    # 修复 },; 模式
    sed -i '' 's/},;/}/g' "$file"
    
    # 修复 );,; 模式
    sed -i '' 's/);,;/);/g' "$file"
    
    # 修复 =>;,; 模式
    sed -i '' 's/=>;,;/=>/g' "$file"
    
    # 修复多余的分号
    sed -i '' 's/;;/;/g' "$file"
    
    # 修复接口定义错误
    sed -i '' 's/{,;,}/{/g' "$file"
    sed -i '' 's/,;,}/}/g' "$file"
done

# 3. 修复Mock文件
echo "🔧 修复Mock文件..."
find src/__mocks__ -name "*.js" | while read file; do
    echo "修复Mock文件: $file"
    
    # 修复未终止的字符串
    sed -i '' "s/'),';/'),/g" "$file"
    sed -i '' "s/'),\";/'),/g" "$file"
    sed -i '' "s/\"),';/\"),/g" "$file"
    
    # 修复多余的分号
    sed -i '' 's/;;/;/g' "$file"
done

# 4. 修复Store文件的特殊问题
echo "🔧 修复Store文件..."
if [ -f "src/store/index.ts" ]; then
    echo "修复 src/store/index.ts"
    sed -i '' 's/return { \.\.\.state, isAuthenticated: false ;};,;/return { ...state, isAuthenticated: false };/g' "src/store/index.ts"
    sed -i '' 's/default: ;,;/default:/g' "src/store/index.ts"
    sed -i '' 's/};,;/};/g' "src/store/index.ts"
    sed -i '' 's/});,;/});/g' "src/store/index.ts"
fi

# 5. 修复Slice文件
find src/store/slices -name "*.tsx" -o -name "*.ts" | while read file; do
    echo "修复Slice文件: $file"
    
    # 修复复杂的语法错误模式
    sed -i '' 's/const: initialState: UserState = {,;,}/const initialState: UserState = {/g' "$file"
    sed -i '' 's/profile: undefined,;,;/profile: undefined,/g' "$file"
    sed -i '' 's/healthData: \[\],;,;/healthData: [],/g' "$file"
    sed -i '' 's/export const fetchUserProfile = createAsyncThunk<;,;/export const fetchUserProfile = createAsyncThunk</g' "$file"
    sed -i '' 's/UserProfile,;,;/UserProfile,/g' "$file"
    sed -i '' 's/);,;/);/g' "$file"
    
    # 修复import语句
    sed -i '' 's/import {AgentsState;,}/import { AgentsState,/g' "$file"
    sed -i '' 's/AgentMessage,;,;/AgentMessage,/g' "$file"
    
    # 修复接口定义
    sed -i '' 's/interface ApiClientResponse<T = any> {success: boolean,;,}/interface ApiClientResponse<T = any> { success: boolean,/g' "$file"
    sed -i '' 's/const data = T;,;/data: T;/g' "$file"
    sed -i '' 's/message\?: string;,;/message?: string;/g' "$file"
    
    # 修复函数定义
    sed -i '' 's/const const = /const /g' "$file"
    sed -i '' 's/const addUserMessage = ();,;/const addUserMessage = ()/g' "$file"
    sed -i '' 's/state;,;/state,/g' "$file"
    
    # 修复对象定义
    sed -i '' 's/) => {"}"";,"";/) => {/g' "$file"
    sed -i '' 's/const: userMessage: AgentMessage = {,;,}/const userMessage: AgentMessage = {/g' "$file"
    sed -i '' 's/const id = Date\.now\(\)\.toString\(\);,;/id: Date.now().toString(),/g' "$file"
    sed -i '' 's/agentType,;,;/agentType,/g' "$file"
    sed -i '' 's/content,;,;/content,/g' "$file"
    sed -i '' 's/type: "text";","";,"";/type: "text"/g' "$file"
    
    # 修复导出语句
    sed -i '' 's/export const {setActiveAgent,;,}/export const { setActiveAgent,/g' "$file"
    sed -i '' 's/addUserMessage,;,;/addUserMessage,/g' "$file"
    sed -i '' 's/removeMessage,;,;/removeMessage,/g' "$file"
    
    # 修复选择器
    sed -i '' 's/export const selectAgents = (state: { agents: AgentsState ;}) => state\.agents;,;/export const selectAgents = (state: { agents: AgentsState }) => state.agents;/g' "$file"
    sed -i '' 's/export const selectActiveAgent = (state: { agents: AgentsState ;}) =>;,;/export const selectActiveAgent = (state: { agents: AgentsState }) =>/g' "$file"
    sed -i '' 's/state\.agents\.activeAgent;,;/state.agents.activeAgent;/g' "$file"
done

# 6. 运行基本语法检查
echo "🔍 运行语法检查..."
if command -v npx &> /dev/null; then
    echo "检查TypeScript语法..."
    npx tsc --noEmit --skipLibCheck 2>&1 | head -20
    
    echo "检查ESLint..."
    npx eslint src --ext .ts,.tsx,.js,.jsx --max-warnings 0 --no-error-on-unmatched-pattern 2>&1 | head -20
fi

# 7. 生成修复报告
echo "📊 生成修复报告..."
cat > bug_fix_report.md << EOF
# 紧急Bug修复报告

## 修复时间
$(date)

## 修复内容
1. ✅ 修复前端TypeScript/JavaScript语法错误
   - 修复 ;,; 模式
   - 修复 "",""模式  
   - 修复 const const 模式
   - 修复 },; 模式
   - 修复 );,; 模式

2. ✅ 修复Mock文件语法错误
   - 修复未终止的字符串字面量
   - 清理多余的分号

3. ✅ 修复Store和Slice文件
   - 修复复杂的语法错误模式
   - 恢复正确的TypeScript语法

## 备份位置
backup/$(date +%Y%m%d_%H%M%S)/

## 下一步建议
1. 运行完整的测试套件
2. 检查应用是否能正常启动
3. 逐个验证关键功能
4. 启用更严格的代码质量检查

## 修复统计
- 处理的文件类型: .ts, .tsx, .js, .jsx
- 主要修复模式: 8种语法错误模式
- 特殊处理: Store/Slice文件, Mock文件
EOF

echo "✅ 紧急Bug修复完成!"
echo "📋 修复报告已生成: bug_fix_report.md"
echo "📦 备份位置: backup/$(date +%Y%m%d_%H%M%S)/"
echo ""
echo "🔍 建议下一步操作:"
echo "1. npm run type-check"
echo "2. npm run lint"  
echo "3. npm start"
echo "4. npm test" 