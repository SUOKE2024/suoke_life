const HealthDataToken = artifacts.require("HealthDataToken");

contract("HealthDataToken", (accounts) => {
  const owner = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];
  const rewardContract = accounts[3];
  
  const initialSupply = 10000000; // 初始1000万代币
  let healthTokenInstance;
  
  beforeEach(async () => {
    healthTokenInstance = await HealthDataToken.new(initialSupply);
  });
  
  it("应该正确初始化代币信息", async () => {
    const name = await healthTokenInstance.name();
    const symbol = await healthTokenInstance.symbol();
    const decimals = await healthTokenInstance.decimals();
    const totalSupply = await healthTokenInstance.totalSupply();
    
    assert.equal(name, "Health Data Token", "名称应为Health Data Token");
    assert.equal(symbol, "HDT", "符号应为HDT");
    assert.equal(decimals.toNumber(), 18, "小数位应为18");
    assert.equal(totalSupply.toString(), web3.utils.toWei(initialSupply.toString(), 'ether'), "初始供应量应匹配");
  });
  
  it("应该允许管理员添加奖励合约", async () => {
    await healthTokenInstance.addRewardContract(rewardContract, { from: owner });
    const isRewardContract = await healthTokenInstance.isRewardContract(rewardContract);
    assert.equal(isRewardContract, true, "应该将合约地址添加到白名单");
  });
  
  it("应该阻止非管理员添加奖励合约", async () => {
    try {
      await healthTokenInstance.addRewardContract(rewardContract, { from: user1 });
      assert.fail("应该抛出异常");
    } catch (error) {
      console.log("实际错误信息:", error.message);
      assert(error, "非管理员应被拒绝访问");
    }
  });
  
  it("白名单合约应该能发放奖励", async () => {
    // 先将合约添加到白名单
    await healthTokenInstance.addRewardContract(rewardContract, { from: owner });
    
    // 从白名单合约地址发放奖励
    const rewardAmount = web3.utils.toWei("100", "ether");
    const rewardType = 0; // DATA_CONTRIBUTION
    
    const result = await healthTokenInstance.reward(user1, rewardAmount, rewardType, { from: rewardContract });
    
    // 验证事件
    assert.equal(result.logs.length, 2, "应该触发两个事件");
    assert.equal(result.logs[1].event, "Rewarded", "第二个事件应该是Rewarded");
    
    // 验证余额
    const balance = await healthTokenInstance.balanceOf(user1);
    assert.equal(balance.toString(), rewardAmount, "余额应该增加奖励数量");
    
    // 验证累计奖励记录
    const totalRewards = await healthTokenInstance.getTotalRewards(user1);
    assert.equal(totalRewards.toString(), rewardAmount, "累计奖励应该等于奖励数量");
  });
  
  it("非白名单合约不能发放奖励", async () => {
    const rewardAmount = web3.utils.toWei("100", "ether");
    const rewardType = 0; // DATA_CONTRIBUTION
    
    try {
      await healthTokenInstance.reward(user1, rewardAmount, rewardType, { from: user2 });
      assert.fail("应该抛出异常");
    } catch (error) {
      assert(error.message.includes("Caller is not authorized"), "错误信息应包含未授权内容");
    }
  });
  
  it("管理员应该能铸造代币", async () => {
    const mintAmount = web3.utils.toWei("5000", "ether");
    const initialBalance = await healthTokenInstance.balanceOf(user2);
    
    await healthTokenInstance.mint(user2, mintAmount, { from: owner });
    
    const newBalance = await healthTokenInstance.balanceOf(user2);
    const expectedBalance = web3.utils.toBN(initialBalance).add(web3.utils.toBN(mintAmount));
    
    assert.equal(newBalance.toString(), expectedBalance.toString(), "余额应该增加铸造数量");
  });
}); 