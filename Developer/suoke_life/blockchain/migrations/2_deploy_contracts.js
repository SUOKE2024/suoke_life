const HealthRecord = artifacts.require("HealthRecord");
const HealthDataToken = artifacts.require("HealthDataToken");

module.exports = async function(deployer, network, accounts) {
  const admin = accounts[0];
  
  // 部署健康记录合约
  await deployer.deploy(HealthRecord);
  console.log("HealthRecord部署地址:", HealthRecord.address);
  
  // 部署健康数据代币合约，只传递初始供应量参数
  await deployer.deploy(HealthDataToken, web3.utils.toWei("1000000", "ether"));
  console.log("HealthDataToken部署地址:", HealthDataToken.address);
  
  // 获取部署后的合约实例
  const healthRecordInstance = await HealthRecord.deployed();
  const healthDataTokenInstance = await HealthDataToken.deployed();
  
  // 将健康记录合约添加为奖励合约（白名单）
  await healthDataTokenInstance.addRewardContract(HealthRecord.address, { from: admin });
  console.log("已将HealthRecord添加为奖励合约");
  
  // 可以在这里添加其他初始化步骤，如设置其他奖励合约或分配初始代币
}; 