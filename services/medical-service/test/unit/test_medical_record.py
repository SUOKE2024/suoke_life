#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
import uuid

from internal.model.medical_record import MedicalRecord, Attachment


class TestMedicalRecord(unittest.TestCase):
    """医疗记录模型单元测试"""
    
    def test_create_medical_record(self):
        """测试创建医疗记录"""
        # 准备测试数据
        user_id = str(uuid.uuid4())
        record_type = "常规检查"
        record_date = datetime.now()
        doctor_id = str(uuid.uuid4())
        doctor_name = "张医生"
        institution = "北京中医医院"
        chief_complaint = "头痛、乏力"
        diagnosis = "感冒"
        treatment = "休息, 服用感冒药"
        notes = "患者需要多休息"
        
        # 创建医疗记录
        record = MedicalRecord.create(
            user_id=user_id,
            record_type=record_type,
            record_date=record_date,
            doctor_id=doctor_id,
            doctor_name=doctor_name,
            institution=institution,
            chief_complaint=chief_complaint,
            diagnosis=diagnosis,
            treatment=treatment,
            notes=notes
        )
        
        # 验证记录
        self.assertEqual(record.user_id, user_id)
        self.assertEqual(record.record_type, record_type)
        self.assertEqual(record.record_date, record_date)
        self.assertEqual(record.doctor_id, doctor_id)
        self.assertEqual(record.doctor_name, doctor_name)
        self.assertEqual(record.institution, institution)
        self.assertEqual(record.chief_complaint, chief_complaint)
        self.assertEqual(record.diagnosis, diagnosis)
        self.assertEqual(record.treatment, treatment)
        self.assertEqual(record.notes, notes)
        self.assertEqual(len(record.attachments), 0)
        self.assertEqual(len(record.metadata), 0)
        self.assertIsNotNone(record.id)
        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)
        self.assertEqual(record.created_at, record.updated_at)
    
    def test_update_medical_record(self):
        """测试更新医疗记录"""
        # 创建医疗记录
        record = MedicalRecord.create(
            user_id=str(uuid.uuid4()),
            record_type="初诊",
            record_date=datetime.now()
        )
        
        # 记录初始更新时间
        initial_updated_at = record.updated_at
        
        # 等待一段时间，确保更新时间不同
        import time
        time.sleep(0.001)
        
        # 更新记录
        new_diagnosis = "高血压"
        record.update(diagnosis=new_diagnosis)
        
        # 验证更新结果
        self.assertEqual(record.diagnosis, new_diagnosis)
        self.assertNotEqual(record.updated_at, initial_updated_at)
    
    def test_add_attachment(self):
        """测试添加附件"""
        # 创建医疗记录
        record = MedicalRecord.create(
            user_id=str(uuid.uuid4()),
            record_type="复诊",
            record_date=datetime.now()
        )
        
        # 创建附件
        attachment = Attachment.create(
            name="血常规检测报告.pdf",
            content_type="application/pdf",
            url="https://example.com/reports/blood_test.pdf",
            size=1024 * 100  # 100KB
        )
        
        # 添加附件
        record.add_attachment(attachment)
        
        # 验证附件
        self.assertEqual(len(record.attachments), 1)
        self.assertEqual(record.attachments[0].name, "血常规检测报告.pdf")
        self.assertEqual(record.attachments[0].content_type, "application/pdf")
        self.assertEqual(record.attachments[0].url, "https://example.com/reports/blood_test.pdf")
        self.assertEqual(record.attachments[0].size, 1024 * 100)
    
    def test_remove_attachment(self):
        """测试移除附件"""
        # 创建医疗记录
        record = MedicalRecord.create(
            user_id=str(uuid.uuid4()),
            record_type="复诊",
            record_date=datetime.now()
        )
        
        # 创建并添加附件
        attachment1 = Attachment.create(
            name="血常规检测报告.pdf",
            content_type="application/pdf",
            url="https://example.com/reports/blood_test.pdf",
            size=1024 * 100
        )
        
        attachment2 = Attachment.create(
            name="X光片.jpg",
            content_type="image/jpeg",
            url="https://example.com/reports/xray.jpg",
            size=1024 * 500
        )
        
        record.add_attachment(attachment1)
        record.add_attachment(attachment2)
        
        # 验证附件数量
        self.assertEqual(len(record.attachments), 2)
        
        # 记录初始更新时间
        initial_updated_at = record.updated_at
        
        # 等待一段时间，确保更新时间不同
        import time
        time.sleep(0.001)
        
        # 移除附件
        result = record.remove_attachment(attachment1.id)
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(len(record.attachments), 1)
        self.assertEqual(record.attachments[0].name, "X光片.jpg")
        self.assertNotEqual(record.updated_at, initial_updated_at)
        
        # 尝试移除不存在的附件
        result = record.remove_attachment("non-existent-id")
        self.assertFalse(result)
    
    def test_metadata(self):
        """测试元数据操作"""
        # 创建医疗记录
        record = MedicalRecord.create(
            user_id=str(uuid.uuid4()),
            record_type="复诊",
            record_date=datetime.now(),
            metadata={"priority": "高", "department": "内科"}
        )
        
        # 验证初始元数据
        self.assertEqual(len(record.metadata), 2)
        self.assertEqual(record.metadata["priority"], "高")
        self.assertEqual(record.metadata["department"], "内科")
        
        # 添加元数据
        record.add_metadata("doctor_specialty", "心脏科")
        
        # 验证添加结果
        self.assertEqual(len(record.metadata), 3)
        self.assertEqual(record.metadata["doctor_specialty"], "心脏科")
        
        # 移除元数据
        result = record.remove_metadata("priority")
        
        # 验证移除结果
        self.assertTrue(result)
        self.assertEqual(len(record.metadata), 2)
        self.assertNotIn("priority", record.metadata)
        
        # 尝试移除不存在的元数据
        result = record.remove_metadata("non-existent-key")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 