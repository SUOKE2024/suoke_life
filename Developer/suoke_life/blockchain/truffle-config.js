/**
 * Use this file to configure your truffle project. It's seeded with some
 * common settings for different networks and features like migrations,
 * compilation, and testing. Uncomment the ones you need or modify
 * them to suit your project as necessary.
 *
 * More information about configuration can be found at:
 *
 * https://trufflesuite.com/docs/truffle/reference/configuration
 *
 * Hands-off deployment with Infura
 * --------------------------------
 *
 * Do you have a complex application that requires lots of transactions to deploy?
 * Use this approach to make deployment a breeze 🏖️:
 *
 * Infura deployment needs a wallet provider (like @truffle/hdwallet-provider)
 * to sign transactions before they're sent to a remote public node.
 * Infura accounts are available for free at 🔍: https://infura.io/register
 *
 * You'll need a mnemonic - the twelve word phrase the wallet uses to generate
 * public/private key pairs. You can store your secrets 🤐 in a .env file.
 * In your project root, run `$ npm install dotenv`.
 * Create .env (which should be .gitignored) and declare your MNEMONIC
 * and Infura PROJECT_ID variables inside.
 * For example, your .env file will have the following structure:
 *
 * MNEMONIC = <Your 12 phrase mnemonic>
 * PROJECT_ID = <Your Infura project id>
 *
 * Deployment with Truffle Dashboard (Recommended for best security practice)
 * --------------------------------------------------------------------------
 *
 * Are you concerned about security and minimizing rekt status 🤔?
 * Use this method for best security:
 *
 * Truffle Dashboard lets you review transactions in detail, and leverages
 * MetaMask for signing, so there's no need to copy-paste your mnemonic.
 * More details can be found at 🔎:
 *
 * https://trufflesuite.com/docs/truffle/getting-started/using-the-truffle-dashboard/
 */

// require('dotenv').config();
// const { MNEMONIC, PROJECT_ID } = process.env;

// const HDWalletProvider = require('@truffle/hdwallet-provider');

/**
 * 索克生活区块链智能合约配置
 */
module.exports = {
  /**
   * 网络配置:
   * development: 本地开发网络
   * testnet: 测试网络 (如Sepolia)
   * mainnet: 主网络
   */
  networks: {
    // 本地开发网络
    development: {
     host: "127.0.0.1",
     port: 8545,
     network_id: "*", // 匹配任何网络ID
    },
    // 本地Ganache UI
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
    },
    // 测试网络配置 (需要添加私钥和API密钥)
    sepolia: {
      // 需要配置HDWalletProvider
      // provider: () => new HDWalletProvider(MNEMONIC, `https://sepolia.infura.io/v3/${PROJECT_ID}`),
      network_id: 11155111, // Sepolia网络ID
      gas: 5500000,
      confirmations: 2, // 等待确认数
      timeoutBlocks: 200, // 超时区块数
      skipDryRun: true, // 跳过dry run
    },
    // 主网配置 (生产环境使用)
    // mainnet: {
    //   // 需要配置HDWalletProvider
    //   // provider: () => new HDWalletProvider(MNEMONIC, `https://mainnet.infura.io/v3/${PROJECT_ID}`),
    //   network_id: 1, // 以太坊主网ID
    //   gas: 5500000,
    //   gasPrice: 20000000000, // 20 Gwei
    //   confirmations: 2,
    //   timeoutBlocks: 200,
    //   skipDryRun: true
    // },
  },

  // 设置默认的mocha测试选项
  mocha: {
    timeout: 100000
  },

  // 配置编译器版本和优化
  compilers: {
    solc: {
      version: "0.8.20", // 使用与安装的solc版本一致或接近的版本
      // docker: true,  // 使用docker版本的solc
      settings: {
        optimizer: {
          enabled: true,
          runs: 200
        },
        evmVersion: "paris" // 默认使用最近的EVM版本
      }
    }
  },

  // db配置
  db: {
    enabled: false
  },

  // 插件配置
  plugins: [
    // 可添加truffle插件，例如 'truffle-plugin-verify'
  ]
};
