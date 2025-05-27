@echo off
setlocal enabledelayedexpansion

echo 🚀 开始安装 Cursor Voice Extension...

REM 检查 Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 Node.js
    echo 请先安装 Node.js: https://nodejs.org/
    pause
    exit /b 1
)

REM 检查 npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到 npm
    pause
    exit /b 1
)

echo ✅ Node.js 和 npm 已安装

REM 检查 Node.js 版本
for /f "tokens=1" %%i in ('node -v') do set NODE_VERSION=%%i
set NODE_VERSION=%NODE_VERSION:v=%

echo ✅ Node.js 版本: %NODE_VERSION%

REM 安装依赖
echo 📦 安装依赖包...
call npm install
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo ✅ 依赖安装完成

REM 编译 TypeScript
echo 🔨 编译 TypeScript...
call npm run compile
if %errorlevel% neq 0 (
    echo ❌ 编译失败
    pause
    exit /b 1
)

echo ✅ 编译完成

REM 检查是否安装了 vsce
where vsce >nul 2>nul
if %errorlevel% neq 0 (
    echo 📦 安装 vsce (VS Code Extension Manager)...
    call npm install -g vsce
)

REM 打包扩展
echo 📦 打包扩展...
call vsce package
if %errorlevel% neq 0 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

echo ✅ 扩展打包完成

REM 查找生成的 .vsix 文件
for %%f in (*.vsix) do set VSIX_FILE=%%f

if not defined VSIX_FILE (
    echo ❌ 未找到 .vsix 文件
    pause
    exit /b 1
)

echo.
echo 🎉 安装完成！
echo.
echo 📁 扩展文件: %VSIX_FILE%
echo.
echo 🔧 下一步操作：
echo 1. 打开 Cursor IDE
echo 2. 按 Ctrl+Shift+P
echo 3. 输入 'Extensions: Install from VSIX'
echo 4. 选择文件: %VSIX_FILE%
echo.
echo 或者运行开发模式：
echo 1. 在 Cursor 中打开此项目文件夹
echo 2. 按 F5 启动扩展开发主机
echo.
echo 📖 详细说明请查看 INSTALLATION_GUIDE.md
echo.
echo 🎤 享受语音编程的乐趣！
echo.
pause 