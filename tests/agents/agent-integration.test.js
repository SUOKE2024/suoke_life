const request = require('supertest');
const { expect } = require('chai');

// 智能体专项集成测试
describe('索克生活智能体集成测试', () => {
  let app;
  let authToken;
  
  before(async () => {
    // 初始化测试环境
    app = require('../../src/app');
    
    // 获取测试用户认证令牌
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        username: 'test_user',
        password: 'test_password'
      });
    
    authToken = loginResponse.body.access_token;
  });

  describe('小艾智能体 (XiaoAi) 测试', () => {
    it('应该能够处理健康咨询请求', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/consult')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          message: '我最近总是感觉疲劳，睡眠质量也不好，该怎么办？',
          user_context: {
            age: 30,
            gender: 'female',
            health_history: []
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('response');
      expect(response.body).to.have.property('suggestions');
      expect(response.body.response).to.be.a('string');
      expect(response.body.suggestions).to.be.an('array');
      
      // 验证响应时间
      expect(response.duration).to.be.below(3000); // 3秒内响应
    });

    it('应该能够提供个性化健康建议', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/personalized-advice')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          health_data: {
            sleep_hours: 6,
            exercise_frequency: 2,
            stress_level: 7,
            diet_quality: 6
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('advice');
      expect(response.body).to.have.property('priority_areas');
      expect(response.body.advice).to.be.an('array');
      expect(response.body.priority_areas).to.be.an('array');
    });

    it('应该能够处理紧急健康情况', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/emergency')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          symptoms: ['胸痛', '呼吸困难', '头晕'],
          severity: 'high'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('urgency_level');
      expect(response.body).to.have.property('immediate_actions');
      expect(response.body.urgency_level).to.be.oneOf(['low', 'medium', 'high', 'critical']);
      expect(response.body.immediate_actions).to.be.an('array');
    });
  });

  describe('小克智能体 (XiaoKe) 测试', () => {
    it('应该能够进行中医体质分析', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoke/constitution-analysis')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          symptoms: ['怕冷', '手脚冰凉', '精神不振', '食欲不振'],
          tongue_image: 'base64_encoded_image',
          pulse_data: {
            rate: 65,
            rhythm: 'regular',
            strength: 'weak'
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('constitution_type');
      expect(response.body).to.have.property('confidence_score');
      expect(response.body).to.have.property('recommendations');
      expect(response.body.confidence_score).to.be.a('number');
      expect(response.body.confidence_score).to.be.within(0, 1);
    });

    it('应该能够推荐中医调理方案', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoke/treatment-plan')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          constitution_type: '阳虚质',
          current_symptoms: ['疲劳', '怕冷', '腰膝酸软'],
          severity: 'moderate'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('herbal_formula');
      expect(response.body).to.have.property('acupuncture_points');
      expect(response.body).to.have.property('lifestyle_advice');
      expect(response.body).to.have.property('duration_weeks');
    });

    it('应该能够解释中医理论', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoke/explain-theory')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          concept: '气血不足',
          detail_level: 'intermediate'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('explanation');
      expect(response.body).to.have.property('related_concepts');
      expect(response.body).to.have.property('practical_applications');
    });
  });

  describe('老克智能体 (LaoKe) 测试', () => {
    it('应该能够进行深度健康分析', async () => {
      const response = await request(app)
        .post('/api/agents/laoke/deep-analysis')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          health_data: {
            vital_signs: {
              blood_pressure: '120/80',
              heart_rate: 72,
              temperature: 36.5
            },
            lab_results: {
              blood_glucose: 5.5,
              cholesterol: 4.2,
              hemoglobin: 140
            },
            symptoms_history: [
              { symptom: '头痛', frequency: 'weekly', duration: '6months' },
              { symptom: '失眠', frequency: 'daily', duration: '3months' }
            ]
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('analysis_report');
      expect(response.body).to.have.property('risk_factors');
      expect(response.body).to.have.property('recommendations');
      expect(response.body).to.have.property('follow_up_schedule');
    });

    it('应该能够制定长期健康管理计划', async () => {
      const response = await request(app)
        .post('/api/agents/laoke/long-term-plan')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          user_profile: {
            age: 45,
            gender: 'male',
            occupation: 'office_worker',
            health_goals: ['减重', '改善睡眠', '降低血压']
          },
          current_health_status: {
            bmi: 26.5,
            blood_pressure: '140/90',
            sleep_quality: 6
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('plan_duration_months');
      expect(response.body).to.have.property('milestones');
      expect(response.body).to.have.property('interventions');
      expect(response.body).to.have.property('monitoring_schedule');
    });

    it('应该能够提供专业医学建议', async () => {
      const response = await request(app)
        .post('/api/agents/laoke/medical-advice')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          medical_question: '糖尿病患者应该如何控制饮食？',
          patient_context: {
            diagnosis: '2型糖尿病',
            duration: '2年',
            current_medication: ['二甲双胍'],
            complications: []
          }
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('medical_advice');
      expect(response.body).to.have.property('evidence_level');
      expect(response.body).to.have.property('contraindications');
      expect(response.body).to.have.property('monitoring_requirements');
    });
  });

  describe('索儿智能体 (Soer) 测试', () => {
    it('应该能够进行儿童健康评估', async () => {
      const response = await request(app)
        .post('/api/agents/soer/child-assessment')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          child_info: {
            age_months: 36,
            gender: 'female',
            weight_kg: 14.5,
            height_cm: 95
          },
          symptoms: ['咳嗽', '流鼻涕', '食欲不振'],
          duration_days: 3
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('assessment');
      expect(response.body).to.have.property('severity_level');
      expect(response.body).to.have.property('care_recommendations');
      expect(response.body).to.have.property('warning_signs');
    });

    it('应该能够提供儿童发育指导', async () => {
      const response = await request(app)
        .post('/api/agents/soer/development-guidance')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          child_age_months: 18,
          current_milestones: {
            walking: true,
            talking_words: 15,
            social_interaction: 'good'
          },
          parent_concerns: ['语言发育', '社交能力']
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('development_status');
      expect(response.body).to.have.property('activities_suggestions');
      expect(response.body).to.have.property('next_milestones');
      expect(response.body).to.have.property('professional_referral');
    });

    it('应该能够处理儿童紧急情况', async () => {
      const response = await request(app)
        .post('/api/agents/soer/emergency-guidance')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          emergency_type: '高热',
          child_age_months: 24,
          symptoms: ['发热39.5°C', '精神萎靡', '拒食'],
          duration_hours: 6
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('urgency_level');
      expect(response.body).to.have.property('immediate_actions');
      expect(response.body).to.have.property('seek_medical_care');
      expect(response.body.seek_medical_care).to.be.a('boolean');
    });
  });

  describe('智能体协作测试', () => {
    it('应该能够进行多智能体协作诊断', async () => {
      const response = await request(app)
        .post('/api/agents/collaborate')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          case_description: '45岁男性，慢性疲劳，睡眠质量差，血压偏高',
          participating_agents: ['xiaoai', 'xiaoke', 'laoke'],
          collaboration_type: 'comprehensive_analysis'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('collaboration_id');
      expect(response.body).to.have.property('agent_contributions');
      expect(response.body).to.have.property('consensus_diagnosis');
      expect(response.body).to.have.property('integrated_recommendations');
      
      // 验证每个智能体都有贡献
      expect(response.body.agent_contributions).to.have.property('xiaoai');
      expect(response.body.agent_contributions).to.have.property('xiaoke');
      expect(response.body.agent_contributions).to.have.property('laoke');
    });

    it('应该能够处理智能体意见分歧', async () => {
      const response = await request(app)
        .post('/api/agents/resolve-conflict')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          case_id: 'test_case_001',
          conflicting_opinions: [
            {
              agent: 'xiaoke',
              diagnosis: '肾阳虚',
              confidence: 0.8
            },
            {
              agent: 'laoke',
              diagnosis: '甲状腺功能减退',
              confidence: 0.7
            }
          ]
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('resolution_strategy');
      expect(response.body).to.have.property('additional_tests_needed');
      expect(response.body).to.have.property('consensus_approach');
    });

    it('应该能够进行智能体学习和改进', async () => {
      const response = await request(app)
        .post('/api/agents/learning-feedback')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          case_id: 'test_case_002',
          actual_outcome: '患者症状改善',
          agent_predictions: {
            xiaoai: { prediction: '需要2周改善', accuracy: 0.9 },
            xiaoke: { prediction: '需要4周改善', accuracy: 0.6 },
            laoke: { prediction: '需要3周改善', accuracy: 0.8 }
          },
          feedback_type: 'outcome_validation'
        });

      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('learning_updates');
      expect(response.body).to.have.property('model_improvements');
      expect(response.body).to.have.property('confidence_adjustments');
    });
  });

  describe('性能和可靠性测试', () => {
    it('应该能够处理并发请求', async () => {
      const concurrentRequests = 10;
      const promises = [];

      for (let i = 0; i < concurrentRequests; i++) {
        promises.push(
          request(app)
            .post('/api/agents/xiaoai/consult')
            .set('Authorization', `Bearer ${authToken}`)
            .send({
              message: `并发测试请求 ${i}`,
              user_context: { age: 30, gender: 'male' }
            })
        );
      }

      const responses = await Promise.all(promises);
      
      // 验证所有请求都成功
      responses.forEach((response, index) => {
        expect(response.status).to.equal(200);
        expect(response.body).to.have.property('response');
      });

      // 验证响应时间合理
      const avgResponseTime = responses.reduce((sum, res) => sum + res.duration, 0) / responses.length;
      expect(avgResponseTime).to.be.below(5000); // 平均5秒内
    });

    it('应该能够处理错误输入', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/consult')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          message: '', // 空消息
          user_context: null // 无效上下文
        });

      expect(response.status).to.equal(400);
      expect(response.body).to.have.property('error');
      expect(response.body.error).to.include('Invalid input');
    });

    it('应该能够处理服务超时', async () => {
      const response = await request(app)
        .post('/api/agents/stress-test')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          complexity_level: 'maximum',
          processing_time: 'extended'
        })
        .timeout(10000); // 10秒超时

      // 应该在超时前返回或优雅处理超时
      if (response.status === 200) {
        expect(response.body).to.have.property('result');
      } else if (response.status === 408) {
        expect(response.body).to.have.property('timeout_handled');
      }
    });
  });

  describe('数据安全和隐私测试', () => {
    it('应该保护用户隐私数据', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/consult')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          message: '我的身份证号是123456789012345678，请帮我分析健康状况',
          user_context: { age: 30, gender: 'male' }
        });

      expect(response.status).to.equal(200);
      // 验证响应中不包含敏感信息
      expect(response.body.response).to.not.include('123456789012345678');
      expect(response.body).to.have.property('privacy_protected', true);
    });

    it('应该验证用户权限', async () => {
      const response = await request(app)
        .post('/api/agents/laoke/medical-advice')
        .send({
          medical_question: '专业医学问题',
          patient_context: {}
        }); // 不提供认证令牌

      expect(response.status).to.equal(401);
      expect(response.body).to.have.property('error');
      expect(response.body.error).to.include('Unauthorized');
    });

    it('应该记录审计日志', async () => {
      const response = await request(app)
        .post('/api/agents/xiaoai/consult')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          message: '测试审计日志',
          user_context: { age: 30, gender: 'male' }
        });

      expect(response.status).to.equal(200);
      expect(response.headers).to.have.property('x-audit-logged');
      expect(response.headers['x-audit-logged']).to.equal('true');
    });
  });

  after(async () => {
    // 清理测试环境
    if (app && app.close) {
      await app.close();
    }
  });
}); 