/**
 * 健康资料模型
 */
const Joi = require('joi');
const config = require('../config');

// 健康资料表名
const TABLE_NAME = 'health_profiles';

// 健康资料验证模式
const createSchema = Joi.object({
  height: Joi.number().min(50).max(250).description('身高（厘米）'),
  weight: Joi.number().min(20).max(300).description('体重（千克）'),
  blood_pressure_systolic: Joi.number().min(60).max(250).description('收缩压（mmHg）'),
  blood_pressure_diastolic: Joi.number().min(40).max(150).description('舒张压（mmHg）'),
  pulse: Joi.number().min(40).max(200).description('脉搏（次/分）'),
  body_temperature: Joi.number().min(35).max(42).description('体温（摄氏度）'),
  blood_sugar: Joi.number().min(2).max(30).description('血糖（mmol/L）'),
  constitution_type: Joi.string().valid(...config.healthProfile.constitutionTypes).description('体质类型'),
  medical_history: Joi.string().max(2000).description('病史'),
  allergies: Joi.string().max(1000).description('过敏史'),
  medications: Joi.string().max(1000).description('用药情况'),
  family_medical_history: Joi.string().max(2000).description('家族病史'),
  privacy_level: Joi.string().valid(...config.healthProfile.privacyLevels).default(config.healthProfile.defaultPrivacyLevel).description('隐私级别')
});

// 健康资料更新验证模式
const updateSchema = Joi.object({
  height: Joi.number().min(50).max(250).description('身高（厘米）'),
  weight: Joi.number().min(20).max(300).description('体重（千克）'),
  blood_pressure_systolic: Joi.number().min(60).max(250).description('收缩压（mmHg）'),
  blood_pressure_diastolic: Joi.number().min(40).max(150).description('舒张压（mmHg）'),
  pulse: Joi.number().min(40).max(200).description('脉搏（次/分）'),
  body_temperature: Joi.number().min(35).max(42).description('体温（摄氏度）'),
  blood_sugar: Joi.number().min(2).max(30).description('血糖（mmol/L）'),
  constitution_type: Joi.string().valid(...config.healthProfile.constitutionTypes).description('体质类型'),
  medical_history: Joi.string().max(2000).description('病史'),
  allergies: Joi.string().max(1000).description('过敏史'),
  medications: Joi.string().max(1000).description('用药情况'),
  family_medical_history: Joi.string().max(2000).description('家族病史'),
  privacy_level: Joi.string().valid(...config.healthProfile.privacyLevels).description('隐私级别')
});

// 体质类型更新验证模式
const constitutionTypeSchema = Joi.object({
  constitutionType: Joi.string().valid(...config.healthProfile.constitutionTypes).required().description('体质类型')
});

// 数据库表结构
const tableStructure = (table) => {
  table.uuid('id').primary();
  table.uuid('user_id').notNullable().unique().references('id').inTable('users').onDelete('CASCADE');
  table.decimal('height', 5, 2).comment('身高(cm)');
  table.decimal('weight', 5, 2).comment('体重(kg)');
  table.integer('blood_pressure_systolic').unsigned().comment('收缩压(mmHg)');
  table.integer('blood_pressure_diastolic').unsigned().comment('舒张压(mmHg)');
  table.integer('pulse').unsigned().comment('脉搏(次/分)');
  table.decimal('body_temperature', 3, 1).comment('体温(°C)');
  table.decimal('blood_sugar', 4, 2).comment('血糖(mmol/L)');
  table.string('constitution_type').comment('体质类型');
  table.text('medical_history').comment('病史');
  table.text('allergies').comment('过敏史');
  table.text('medications').comment('用药情况');
  table.text('family_medical_history').comment('家族病史');
  table.enum('privacy_level', ['private', 'shared_doctor', 'shared_family', 'shared_researcher', 'public']).defaultTo('private');
  table.timestamp('created_at').defaultTo(table.fn.now());
  table.timestamp('updated_at').defaultTo(table.fn.now());
  table.timestamp('last_checkup');
  
  // 索引
  table.index('constitution_type');
};

module.exports = {
  TABLE_NAME,
  createSchema,
  updateSchema,
  constitutionTypeSchema,
  tableStructure
}; 