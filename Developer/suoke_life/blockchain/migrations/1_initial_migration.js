const HealthRecord = artifacts.require("HealthRecord");
const HealthDataToken = artifacts.require("HealthDataToken");

module.exports = async function (deployer, network, accounts) {
  // 部署健康数据记录合约
  await deployer.deploy(HealthRecord);
  console.log("HealthRecord部署地址:", HealthRecord.address);
  
  // 部署健康数据代币 - 初始供应量10,000,000枚
  const initialSupply = 10000000; 
  await deployer.deploy(HealthDataToken, initialSupply);
  console.log("HealthDataToken部署地址:", HealthDataToken.address);
  
  // 可以在这里添加更多的部署后初始化逻辑
  // 例如，设置权限、执行初始铸币等
}; 