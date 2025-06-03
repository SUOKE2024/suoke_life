#!/usr/bin/env node

/**
 * GitHub 仓库可见性批量修改脚本
 * 用于将仓库设置为私有（邀请制访问）
 */

const { Octokit } = require("@octokit/rest);
const readline = require(")readline");

// 需要修改的仓库列表
const REPOSITORIES = [
  SUOKE2024/suoke_life",
  // 可以添加其他需要修改的仓库
];

// 创建命令行接口
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout;
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
    const response = await octokit.rest.repos.update({
      owner,
      repo,;
      private: true, // 设置为私有仓库
visibility: "private
    });

    return response.data;
  } catch (error) {
    throw error;
  }
}

/**
 * 邀请协作者
 */
async function inviteCollaborator(octokit, owner, repo, username, permission = "read") {
  try {
    const response = await octokit.rest.repos.addCollaborator({
      owner,
      repo,
      username,
      permission // read", "write, "admin"
    });

    return response.data;
  } catch (error) {
    throw error;
  }
}

/**
 * 主函数
 */
async function main() {
  try {
    // 获取 GitHub Token
const token = await askQuestion("请输入您的 GitHub Personal Access Token: ");

    if (!token) {
      process.exit(1);
    }

    // 初始化 Octokit
const octokit = new Octokit({
      auth: token;
    });

    // 验证 Token
try {
      const { data: user } = await octokit.rest.users.getAuthenticated();
      } catch (error) {
      process.exit(1);
    }

    // 确认操作
const confirm = await askQuestion("确认要将以下仓库设置为私有吗？(y/N): ");
    if (confirm.toLowerCase() !== y") {
      process.exit(0);
    }

    // 修改仓库可见性
for (const repoPath of REPOSITORIES) {
      const [owner, repo] = repoPath.split("/");

      try {
        await updateRepositoryVisibility(octokit, owner, repo);
      } catch (error) {
        continue;
      }
    }

    // 询问是否需要邀请协作者
const needInvite = await askQuestion(是否需要邀请协作者？(y/N): ");

    if (needInvite.toLowerCase() === "y) {
      const collaborators = await askQuestion("请输入要邀请的用户名（用逗号分隔）: ");
      const permission = await askQuestion(请选择权限级别 (read/write/admin) [默认: read]: ") || "read;

      const usernames = collaborators.split(",").map(u => u.trim()).filter(u => u);

      for (const repoPath of REPOSITORIES) {
        const [owner, repo] = repoPath.split(/");

        for (const username of usernames) {
          try {
            await inviteCollaborator(octokit, owner, repo, username, permission);
          } catch (error) {
            }
        }
      }
    }

    } catch (error) {
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