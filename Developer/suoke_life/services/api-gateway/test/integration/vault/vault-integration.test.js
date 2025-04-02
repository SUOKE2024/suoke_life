const { describe, it, before, after } = require('mocha');
const { expect } = require('chai');
const sinon = require('sinon');
const axios = require('axios');
const vaultConfig = require('../../../src/config/vault-config');

describe('Vault集成测试', () => {
  let axiosStub;
  
  before(() => {
    // 模拟Vault响应
    axiosStub = sinon.stub(axios, 'get').resolves({
      status: 200,
      data: {
        data: {
          data: {
            services: {
              agentCoordinatorService: {
                instances: ['http://agent-coordinator-service:80'],
                prefix: '/api/v1/agents/coordinator'
              }
            },
            security: {
              apiKeyRequired: true
            }
          }
        }
      }
    });
    
    process.env.VAULT_ENABLED = 'true';
    process.env.VAULT_TOKEN = 'test-token';
  });
  
  after(() => {
    axiosStub.restore();
    delete process.env.VAULT_ENABLED;
    delete process.env.VAULT_TOKEN;
  });
  
  it('应该能从Vault获取配置', async () => {
    await vaultConfig.initialize();
    const config = await vaultConfig.getConfig();
    
    expect(config).to.have.property('services');
    expect(config.services).to.have.property('agentCoordinatorService');
    expect(config.services.agentCoordinatorService).to.have.property('instances').that.is.an('array');
  });
  
  it('应该能获取特定配置项', async () => {
    const apiKeyRequired = await vaultConfig.getConfigValue('security.apiKeyRequired');
    expect(apiKeyRequired).to.be.true;
  });
});