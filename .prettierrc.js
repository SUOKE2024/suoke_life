module.exports = {
  // 基本格式设置
  semi: true,                    // 使用分号
  trailingComma: "es5",         // 在ES5中有效的尾随逗号
  singleQuote: true,            // 使用单引号
  doubleQuote: false,           // 不使用双引号
  quoteProps: "as-needed",      // 仅在需要时为对象属性添加引号
  
  // 缩进设置
  tabWidth: 2,                  // 缩进宽度为2个空格
  useTabs: false,               // 使用空格而不是制表符
  
  // 行宽设置
  printWidth: 100,              // 行宽限制为100字符
  
  // JSX设置
  jsxSingleQuote: true,         // JSX中使用单引号
  jsxBracketSameLine: false,    // JSX标签的>不与最后一行属性放在同一行
  
  // 箭头函数参数
  arrowParens: "avoid",         // 单参数箭头函数省略括号
  
  // 换行符
  endOfLine: "lf",              // 使用LF换行符
  
  // HTML空格敏感性
  htmlWhitespaceSensitivity: "css",
  
  // 嵌入代码格式化
  embeddedLanguageFormatting: "auto",
  
  // 文件覆盖设置
  overrides: [
    {
      files: "*.{js,jsx,ts,tsx}",
      options: {
        parser: "typescript",
        semi: true,
        singleQuote: true,
        trailingComma: "es5",
        printWidth: 100,
        tabWidth: 2,
        useTabs: false,
        bracketSpacing: true,
        arrowParens: "avoid",
        endOfLine: "lf"
      }
    },
    {
      files: "*.json",
      options: {
        parser: "json",
        printWidth: 100,
        tabWidth: 2,
        useTabs: false,
        trailingComma: "none"
      }
    },
    {
      files: "*.md",
      options: {
        parser: "markdown",
        printWidth: 80,
        proseWrap: "preserve",
        tabWidth: 2,
        useTabs: false
      }
    },
    {
      files: "*.{yml,yaml}",
      options: {
        parser: "yaml",
        printWidth: 100,
        tabWidth: 2,
        useTabs: false,
        singleQuote: true
      }
    }
  ]
}; 