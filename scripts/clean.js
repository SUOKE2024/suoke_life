const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

// 颜色设置
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
};

// 日志函数
const log = {
  info: (msg) => console.log(`${colors.blue}${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✓ ${msg}${colors.reset}`),
  warn: (msg) => console.log(`${colors.yellow}${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}${msg}${colors.reset}`),
  title: (msg) => console.log(`\n${colors.bright}${colors.magenta}${msg}${colors.reset}\n`),
};

// 创建问答界面
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 执行命令的函数
function exec(command, options = {}) {
  try {
    execSync(command, {
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options,
    });
    return true;
  } catch (error) {
    if (!options.ignoreError) {
      log.error(`执行命令失败: ${command}`);
      if (error.stdout) console.log(error.stdout.toString());
      if (error.stderr) console.log(error.stderr.toString());
    }
    return false;
  }
}

// 删除目录/文件函数
function removePath(pathToRemove, options = {}) {
  if (!fs.existsSync(pathToRemove)) return;
  
  if (options.silent !== true) {
    log.info(`正在删除: ${pathToRemove}`);
  }
  
  try {
    if (fs.lstatSync(pathToRemove).isDirectory()) {
      exec(`rm -rf "${pathToRemove}"`, { silent: options.silent });
    } else {
      fs.unlinkSync(pathToRemove);
    }
    return true;
  } catch (error) {
    if (!options.silent) {
      log.error(`无法删除: ${pathToRemove}`);
    }
    return false;
  }
}

// 清理函数
const cleaners = {
  // 前端缓存清理
  reactNative: () => {
    log.title('清理 React Native 缓存');
    
    log.info('清理 Metro 缓存...');
    removePath('/tmp/metro-*');
    removePath('/tmp/react-*');
    removePath('/tmp/haste-*');
    removePath('/tmp/metro-bundler-cache-*');
    exec('watchman watch-del-all', { ignoreError: true });
    log.success('Metro 缓存已清理');
    
    log.info('清理 Watchman 缓存...');
    removePath('.watchman-cookie-*');
    log.success('Watchman 缓存已清理');
    
    log.info('清理 ESLint 缓存...');
    removePath('.eslintcache');
    log.success('ESLint 缓存已清理');
    
    return true;
  },
  
  nodeModules: () => {
    log.title('清理 Node 模块');
    removePath('node_modules');
    removePath('package-lock.json');
    removePath('yarn.lock');
    log.success('Node 模块已清理');
    return true;
  },
  
  ios: () => {
    log.title('清理 iOS 缓存');
    removePath('ios/build');
    removePath('ios/Pods');
    removePath('ios/Podfile.lock');
    removePath('ios/*.xcworkspace/xcuserdata');
    removePath('ios/*.xcodeproj/xcuserdata');
    removePath('ios/*.xcodeproj/project.xcworkspace/xcuserdata');
    removePath('ios/SuokeLife/main.jsbundle*');
    log.success('iOS 缓存已清理');
    return true;
  },
  
  android: () => {
    log.title('清理 Android 缓存');
    removePath('android/app/build');
    removePath('android/build');
    removePath('android/.gradle');
    removePath('android/app/src/main/assets/index.android.bundle');
    removePath('android/app/src/main/res/drawable-*');
    removePath('android/app/src/main/res/raw');
    log.success('Android 缓存已清理');
    return true;
  },
  
  temp: () => {
    log.title('清理临时文件');
    removePath('temp/*');
    log.success('临时文件已清理');
    return true;
  },
  
  // 服务端缓存清理
  pythonVenv: () => {
    log.title('清理 Python 虚拟环境');
    const services = [
      'services/accessibility-service/venv',
      'services/api-gateway/venv',
    ];
    
    services.forEach(service => {
      if (fs.existsSync(service)) {
        log.info(`清理 ${service}...`);
        removePath(service);
      }
    });
    
    log.success('Python 虚拟环境已清理');
    return true;
  },
  
  pythonCache: () => {
    log.title('清理 Python 缓存');
    
    // 查找和删除所有 __pycache__ 目录和 .pyc 文件
    log.info('正在查找 __pycache__ 目录和 .pyc 文件...');
    
    // 使用 find 命令查找
    try {
      // 删除所有 __pycache__ 目录
      exec('find ./services -type d -name "__pycache__" -exec rm -rf {} +', { silent: true });
      
      // 删除所有 .pyc 文件
      exec('find ./services -name "*.pyc" -delete', { silent: true });
      
      log.success('Python 缓存已清理');
    } catch (error) {
      log.error('清理 Python 缓存时出错');
      return false;
    }
    
    return true;
  },
  
  dockerImages: () => {
    log.title('清理 Docker 镜像和容器');
    log.warn('此操作将删除所有未使用的 Docker 镜像和容器，包括其他项目的镜像');
    
    const response = process.argv.includes('--yes') ? 'y' : undefined;
    
    const proceed = () => {
      try {
        // 停止所有运行中的容器
        log.info('停止所有 Suoke 相关的 Docker 容器...');
        exec('docker ps -a | grep suoke | awk \'{print $1}\' | xargs -r docker stop', { silent: true, ignoreError: true });
        
        // 删除所有停止的容器
        log.info('删除所有停止的容器...');
        exec('docker container prune -f', { silent: true });
        
        // 删除所有悬空的镜像
        log.info('删除所有悬空的镜像...');
        exec('docker image prune -f', { silent: true });
        
        log.success('Docker 缓存已清理');
        return true;
      } catch (error) {
        log.error('清理 Docker 时出错');
        return false;
      }
    };

    if (response === 'y') {
      return proceed();
    } else {
      return new Promise(resolve => {
        rl.question('确定要清理 Docker 缓存吗? (y/n): ', (answer) => {
          if (answer.toLowerCase() === 'y') {
            resolve(proceed());
          } else {
            log.warn('已跳过 Docker 缓存清理');
            resolve(false);
          }
        });
      });
    }
  },
  
  all: async () => {
    log.title('全面清理所有缓存');
    
    cleaners.reactNative();
    cleaners.nodeModules();
    cleaners.ios();
    cleaners.android();
    cleaners.temp();
    cleaners.pythonVenv();
    cleaners.pythonCache();
    await cleaners.dockerImages();
    
    log.title('缓存清理完成！');
    log.warn('请记得运行 npm install 重新安装依赖');
    
    return true;
  }
};

// 显示帮助信息
function showHelp() {
  console.log(`
${colors.bright}Suoke Life 项目缓存清理工具${colors.reset}

使用方法:
  node scripts/clean.js [选项]

选项:
  --react-native    清理 React Native 相关缓存
  --node-modules    清理 Node 模块
  --ios             清理 iOS 构建缓存
  --android         清理 Android 构建缓存
  --temp            清理临时文件
  --python-venv     清理 Python 虚拟环境
  --python-cache    清理 Python 缓存文件 (__pycache__, .pyc)
  --docker          清理相关 Docker 镜像和容器
  --all             清理所有缓存
  --yes             自动确认所有操作
  --help            显示帮助信息

示例:
  node scripts/clean.js --react-native --ios
  node scripts/clean.js --all --yes
  `);
}

// 主函数
async function main() {
  // 处理参数
  const args = process.argv.slice(2);
  
  // 如果没有参数或有帮助参数，显示帮助信息
  if (args.length === 0 || args.includes('--help')) {
    showHelp();
    rl.close();
    return;
  }
  
  // 处理各个清理选项
  const cleanOptions = {
    '--react-native': 'reactNative',
    '--node-modules': 'nodeModules', 
    '--ios': 'ios',
    '--android': 'android',
    '--temp': 'temp',
    '--python-venv': 'pythonVenv',
    '--python-cache': 'pythonCache',
    '--docker': 'dockerImages',
    '--all': 'all'
  };
  
  let hasRun = false;
  
  // 运行选定的清理函数
  for (const [arg, funcName] of Object.entries(cleanOptions)) {
    if (args.includes(arg)) {
      hasRun = true;
      await cleaners[funcName]();
    }
  }
  
  // 如果没有匹配的清理选项
  if (!hasRun) {
    log.error('未指定有效的清理选项。请使用 --help 查看帮助。');
  }
  
  rl.close();
}

// 运行主函数
main(); 