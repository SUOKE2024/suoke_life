#!/usr/bin/env node

/**
 * GitHub 仓库可见性批量修改脚本
 * 用于将仓库设置为私有（邀请制访问）
 */

const { Octokit } = require('@octokit/rest');
const readline = require('readline');

// 需要修改的仓库列表
const REPOSITORIES = [
  'SUOKE2024/suoke_life',
  // 可以添加其他需要修改的仓库
];

// 创建命令行接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * 获取用户输入
 */
function askQuestion(question) {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
}

/**
 * 修改仓库可见性
 */
async function updateRepositoryVisibility(octokit, owner, repo) {
  try {
    console.log(`正在修改仓库 ${owner}/${repo} 的可见性...`);
    
    const response = await octokit.rest.repos.update({
      owner,
      repo,
      private: true, // 设置为私有仓库
      visibility: 'private'
    });
    
    console.log(`✅ 成功将 ${owner}/${repo} 设置为私有仓库`);
    return response.data;
  } catch (error) {
    console.error(`❌ 修改 ${owner}/${repo} 失败:`, error.message);
    throw error;
  }
}

/**
 * 邀请协作者
 */
async function inviteCollaborator(octokit, owner, repo, username, permission = 'read') {
  try {
    console.log(`正在邀请 ${username} 作为 ${owner}/${repo} 的协作者...`);
    
    const response = await octokit.rest.repos.addCollaborator({
      owner,
      repo,
      username,
      permission // 'read', 'write', 'admin'
    });
    
    console.log(`✅ 成功邀请 ${username} 作为协作者`);
    return response.data;
  } catch (error) {
    console.error(`❌ 邀请 ${username} 失败:`, error.message);
    throw error;
  }
}

/**
 * 主函数
 */
async function main() {
  try {
    console.log('🚀 GitHub 仓库可见性修改工具');
    console.log('================================');
    
    // 获取 GitHub Token
    const token = await askQuestion('请输入您的 GitHub Personal Access Token: ');
    
    if (!token) {
      console.error('❌ 需要提供 GitHub Token');
      process.exit(1);
    }
    
    // 初始化 Octokit
    const octokit = new Octokit({
      auth: token
    });
    
    // 验证 Token
    try {
      const { data: user } = await octokit.rest.users.getAuthenticated();
      console.log(`✅ 已认证用户: ${user.login}`);
    } catch (error) {
      console.error('❌ Token 验证失败:', error.message);
      process.exit(1);
    }
    
    // 确认操作
    const confirm = await askQuestion('确认要将以下仓库设置为私有吗？(y/N): ');
    if (confirm.toLowerCase() !== 'y') {
      console.log('操作已取消');
      process.exit(0);
    }
    
    // 修改仓库可见性
    for (const repoPath of REPOSITORIES) {
      const [owner, repo] = repoPath.split('/');
      
      try {
        await updateRepositoryVisibility(octokit, owner, repo);
      } catch (error) {
        console.error(`跳过仓库 ${repoPath}: ${error.message}`);
        continue;
      }
    }
    
    // 询问是否需要邀请协作者
    const needInvite = await askQuestion('是否需要邀请协作者？(y/N): ');
    
    if (needInvite.toLowerCase() === 'y') {
      const collaborators = await askQuestion('请输入要邀请的用户名（用逗号分隔）: ');
      const permission = await askQuestion('请选择权限级别 (read/write/admin) [默认: read]: ') || 'read';
      
      const usernames = collaborators.split(',').map(u => u.trim()).filter(u => u);
      
      for (const repoPath of REPOSITORIES) {
        const [owner, repo] = repoPath.split('/');
        
        for (const username of usernames) {
          try {
            await inviteCollaborator(octokit, owner, repo, username, permission);
          } catch (error) {
            console.error(`邀请 ${username} 到 ${repoPath} 失败: ${error.message}`);
          }
        }
      }
    }
    
    console.log('\n🎉 操作完成！');
    console.log('\n📋 后续步骤：');
    console.log('1. 被邀请的用户需要接受邀请才能访问仓库');
    console.log('2. 您可以在 GitHub 仓库设置中管理协作者权限');
    console.log('3. 私有仓库的 CI/CD 可能需要重新配置访问权限');
    
  } catch (error) {
    console.error('❌ 操作失败:', error.message);
    process.exit(1);
  } finally {
    rl.close();
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  updateRepositoryVisibility,
  inviteCollaborator
}; 