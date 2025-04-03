/**
 * 生成测试用户数据
 */
const bcrypt = require('bcrypt');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// 解析命令行参数
const argv = yargs(hideBin(process.argv))
  .option('count', {
    alias: 'c',
    description: '生成的测试用户数量',
    type: 'number',
    default: 100
  })
  .option('output', {
    alias: 'o',
    description: '输出文件路径',
    type: 'string',
    default: path.join(__dirname, '../test/fixtures/test-users.json')
  })
  .help()
  .alias('help', 'h')
  .argv;

// 名字列表
const firstNames = [
  '张', '李', '王', '赵', '刘', '陈', '杨', '黄', '周', '吴',
  '郑', '孙', '马', '朱', '胡', '林', '郭', '何', '高', '罗',
  '梁', '宋', '郝', '唐', '许', '邓', '冯', '韩', '曹', '曾'
];

const lastNames = [
  '伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '洋',
  '艳', '勇', '军', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
  '平', '刚', '桂英', '玉兰', '志强', '建华', '建国', '小红', '小明', '小刚'
];

// 随机获取数组中的一个元素
function getRandomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// 生成随机手机号
function generatePhoneNumber() {
  const prefixes = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                    '150', '151', '152', '153', '155', '156', '157', '158', '159',
                    '180', '181', '182', '183', '184', '185', '186', '187', '188', '189'];
  
  const prefix = getRandomElement(prefixes);
  const suffix = Math.floor(Math.random() * 100000000).toString().padStart(8, '0');
  
  return prefix + suffix;
}

// 生成随机邮箱
function generateEmail(username) {
  const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', '163.com', 'qq.com', 'suoke.life'];
  const domain = getRandomElement(domains);
  
  return `${username}@${domain}`;
}

// 生成随机密码
function generatePassword() {
  const length = 10 + Math.floor(Math.random() * 6); // 10-15位密码
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+';
  
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  
  // 确保密码包含至少一个大写字母、小写字母、数字和特殊字符
  password += 'A1!a';
  
  return password;
}

// 生成用户数据
async function generateUsers(count) {
  const users = [];
  
  console.log(`正在生成 ${count} 个测试用户...`);
  
  for (let i = 0; i < count; i++) {
    const id = uuidv4();
    const firstName = getRandomElement(firstNames);
    const lastName = getRandomElement(lastNames);
    const username = `user_${firstName}${lastName}_${Math.floor(Math.random() * 10000)}`;
    const email = generateEmail(username.toLowerCase());
    const phone = generatePhoneNumber();
    const password = generatePassword();
    const hashedPassword = await bcrypt.hash(password, 10);
    
    users.push({
      id,
      username,
      email,
      phone,
      password: hashedPassword,
      plainPassword: password, // 仅用于测试
      firstName,
      lastName,
      role: Math.random() > 0.9 ? 'admin' : 'user',
      status: Math.random() > 0.95 ? 'disabled' : 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
    
    if ((i + 1) % 10 === 0) {
      process.stdout.write(`已生成 ${i + 1} 个用户...\r`);
    }
  }
  
  console.log(`\n${count} 个测试用户生成完成!`);
  
  return users;
}

// 主函数
async function main() {
  try {
    const users = await generateUsers(argv.count);
    
    // 确保输出目录存在
    const outputDir = path.dirname(argv.output);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 写入文件
    fs.writeFileSync(argv.output, JSON.stringify(users, null, 2));
    
    console.log(`测试用户数据已写入: ${argv.output}`);
    
    // 打印摘要
    console.log('\n用户数据摘要:');
    console.log(`- 总用户数: ${users.length}`);
    console.log(`- 管理员用户: ${users.filter(u => u.role === 'admin').length}`);
    console.log(`- 普通用户: ${users.filter(u => u.role === 'user').length}`);
    console.log(`- 已禁用用户: ${users.filter(u => u.status === 'disabled').length}`);
    
    // 打印几个示例用户用于测试
    console.log('\n示例用户 (用于测试):');
    for (let i = 0; i < Math.min(5, users.length); i++) {
      const user = users[i];
      console.log(`用户 #${i+1}:`);
      console.log(`- 用户名: ${user.username}`);
      console.log(`- 邮箱: ${user.email}`);
      console.log(`- 密码: ${user.plainPassword}`);
      console.log(`- 角色: ${user.role}`);
      console.log('');
    }
  } catch (error) {
    console.error('生成测试用户失败:', error);
    process.exit(1);
  }
}

// 执行主函数
main();