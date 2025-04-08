const HealthRecord = artifacts.require("HealthRecord");

contract("HealthRecord", (accounts) => {
  const owner = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];
  
  let healthRecordInstance;
  
  beforeEach(async () => {
    healthRecordInstance = await HealthRecord.new();
  });
  
  it("应该能创建健康记录", async () => {
    const dataHash = "QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn";
    const dataType = "舌诊";
    const metadata = "加密的元数据信息";
    
    const result = await healthRecordInstance.createRecord(
      dataHash,
      dataType,
      metadata,
      { from: owner }
    );
    
    // 验证事件被触发
    assert.equal(result.logs.length, 1, "应该触发一个事件");
    assert.equal(result.logs[0].event, "RecordCreated", "应该是RecordCreated事件");
    
    // 验证记录数量
    const recordCount = await healthRecordInstance.getUserRecordCount({ from: owner });
    assert.equal(recordCount, 1, "用户应该有一条记录");
    
    // 获取记录ID
    const recordId = await healthRecordInstance.getUserRecordIdAtIndex(0, { from: owner });
    
    // 获取记录详情
    const record = await healthRecordInstance.getRecord(recordId, { from: owner });
    
    assert.equal(record.dataHash, dataHash, "数据哈希应该匹配");
    assert.equal(record.dataType, dataType, "数据类型应该匹配");
    assert.equal(record.isShared, false, "初始状态下记录不应该被共享");
  });
  
  it("应该能共享记录给其他用户", async () => {
    // 先创建记录
    const dataHash = "QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn";
    const dataType = "面诊";
    const metadata = "加密的面诊数据";
    
    await healthRecordInstance.createRecord(
      dataHash,
      dataType,
      metadata,
      { from: owner }
    );
    
    const recordId = await healthRecordInstance.getUserRecordIdAtIndex(0, { from: owner });
    
    // 共享记录给user1
    const shareResult = await healthRecordInstance.shareRecord(recordId, user1, { from: owner });
    
    // 验证共享事件
    assert.equal(shareResult.logs.length, 1, "应该触发一个事件");
    assert.equal(shareResult.logs[0].event, "RecordShared", "应该是RecordShared事件");
    
    // 验证user1可以访问记录
    const record = await healthRecordInstance.getRecord(recordId, { from: user1 });
    assert.equal(record.dataHash, dataHash, "授权用户应该能查看数据");
    assert.equal(record.isShared, true, "记录状态应该是已共享");
  });
  
  it("未授权用户应该无法访问记录", async () => {
    // 先创建记录
    const dataHash = "QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn";
    const dataType = "舌诊";
    const metadata = "加密数据";
    
    await healthRecordInstance.createRecord(
      dataHash,
      dataType,
      metadata,
      { from: owner }
    );
    
    const recordId = await healthRecordInstance.getUserRecordIdAtIndex(0, { from: owner });
    
    // 未授权用户user2尝试访问记录应该失败
    try {
      await healthRecordInstance.getRecord(recordId, { from: user2 });
      assert.fail("应该抛出异常");
    } catch (error) {
      assert(error.message.includes("Not authorized"), "错误消息应包含'Not authorized'");
    }
  });
}); 