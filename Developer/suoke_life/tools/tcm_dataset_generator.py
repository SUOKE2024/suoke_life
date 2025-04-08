#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活TCM数据集生成工具
用于为RAG服务生成测试数据集
"""

import os
import json
import argparse
import random
import datetime
from typing import Dict, List, Any, Optional


class TCMDatasetGenerator:
    """TCM数据集生成器类"""

    def __init__(self, output_dir: str, sample_size: int = 100, random_seed: Optional[int] = None):
        """
        初始化TCM数据集生成器
        :param output_dir: 输出目录
        :param sample_size: 样本大小
        :param random_seed: 随机种子
        """
        self.output_dir = output_dir
        self.sample_size = sample_size
        
        if random_seed is not None:
            random.seed(random_seed)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 舌诊类型数据
        self.tongue_types = [
            "淡白舌", "淡红舌", "红舌", "绛舌", "紫舌", "青舌", "灰黑舌"
        ]
        
        # 舌苔类型数据
        self.tongue_coating_types = [
            "薄白苔", "厚白苔", "黄苔", "厚黄苔", "灰苔", "黑苔", "腻苔", "干苔", "剥苔", "无苔"
        ]
        
        # 脉象类型数据
        self.pulse_types = [
            "浮脉", "沉脉", "迟脉", "数脉", "虚脉", "实脉", "滑脉", "涩脉", "弦脉", "细脉", 
            "洪脉", "微脉", "紧脉", "缓脉", "芤脉", "濡脉", "革脉", "牢脉", "长脉", "短脉", 
            "代脉", "促脉", "结脉", "动脉", "伏脉"
        ]
        
        # 面色类型数据
        self.face_color_types = [
            "面色淡白", "面色潮红", "面色晦暗", "面色青白", "面色黄", "面色黄而明亮", 
            "面色萎黄", "面色黧黑", "面色黑", "面色青", "面色青黑", "面色红黑"
        ]
        
        # 体质类型数据
        self.constitution_types = [
            "平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"
        ]
        
        # 中医证型数据
        self.syndrome_types = [
            "风寒证", "风热证", "风湿证", "寒证", "热证", "暑证", "湿证", "燥证", "火证", 
            "气虚证", "气陷证", "气滞证", "气逆证", "血虚证", "血瘀证", "阳虚证", "阴虚证", 
            "痰证", "痰饮证", "水饮证", "内热证", "血热证", "津液亏虚"
        ]
        
        # 常见中药数据
        self.herbs = [
            "人参", "黄芪", "白术", "茯苓", "甘草", "当归", "川芎", "白芍", "熟地黄", "生地黄", 
            "黄连", "黄芩", "黄柏", "栀子", "金银花", "连翘", "板蓝根", "大青叶", "柴胡", "前胡", 
            "葛根", "桔梗", "麻黄", "杏仁", "薄荷", "荆芥", "防风", "羌活", "独活", "藁本", 
            "枳实", "枳壳", "陈皮", "半夏", "天麻", "白芷", "蝉蜕", "牛蒡子", "桑叶", "菊花", 
            "石膏", "知母", "生姜", "干姜", "肉桂", "附子", "细辛", "艾叶", "丹参", "红花"
        ]
        
        # 常见方剂数据
        self.formulas = [
            "四君子汤", "四物汤", "六味地黄丸", "八珍汤", "十全大补汤", "补中益气汤", "玉屏风散", 
            "人参养营汤", "归脾汤", "炙甘草汤", "当归补血汤", "麦门冬汤", "沙参麦冬汤", "生脉散", 
            "百合固金汤", "清营汤", "清瘟败毒饮", "银翘散", "桑菊饮", "桂枝汤", "麻黄汤", "小青龙汤", 
            "大青龙汤", "葛根汤", "升麻葛根汤", "防风通圣散", "消风散", "羌活胜湿汤", "苍术导痰汤", 
            "二陈汤", "温胆汤", "半夏白术天麻汤", "安宫牛黄丸", "紫雪散", "黄连解毒汤", "导赤散", 
            "泻白散", "泻黄散", "左金丸", "柴胡疏肝散", "逍遥散", "四逆散", "小柴胡汤", "大柴胡汤", 
            "五苓散", "猪苓汤", "真武汤", "苓桂术甘汤", "桂枝甘草龙骨牡蛎汤", "甘麦大枣汤"
        ]

    def generate_tongue_dataset(self) -> List[Dict[str, Any]]:
        """
        生成舌诊数据集
        :return: 舌诊数据集
        """
        dataset = []
        for _ in range(self.sample_size):
            tongue_type = random.choice(self.tongue_types)
            tongue_coating = random.choice(self.tongue_coating_types)
            pulse_type = random.choice(self.pulse_types)
            syndrome = random.choice(self.syndrome_types)
            constitution = random.choice(self.constitution_types)
            herbs = random.sample(self.herbs, k=random.randint(3, 8))
            formulas = random.sample(self.formulas, k=random.randint(1, 3))
            
            # 生成特征描述
            features = []
            if random.random() > 0.5:
                features.append("舌体" + random.choice(["胖大", "瘦小", "正常"]))
            if random.random() > 0.5:
                features.append("舌" + random.choice(["有齿痕", "无齿痕"]))
            if random.random() > 0.5:
                features.append("舌尖" + random.choice(["红", "暗红", "紫", "正常"]))
            if random.random() > 0.5:
                features.append("舌苔" + random.choice(["滑", "腻", "干", "燥", "剥落"]))
            
            entry = {
                "id": f"tongue_{_:04d}",
                "tongue_type": tongue_type,
                "tongue_coating": tongue_coating,
                "pulse_type": pulse_type,
                "syndrome": syndrome,
                "constitution": constitution,
                "herbs": herbs,
                "formulas": formulas,
                "features": features,
                "description": f"该患者舌象为{tongue_type}，{tongue_coating}，脉象为{pulse_type}，辨证为{syndrome}。",
                "timestamp": datetime.datetime.now().isoformat()
            }
            dataset.append(entry)
        
        return dataset

    def generate_pulse_dataset(self) -> List[Dict[str, Any]]:
        """
        生成脉诊数据集
        :return: 脉诊数据集
        """
        dataset = []
        for _ in range(self.sample_size):
            pulse_type = random.choice(self.pulse_types)
            pulse_strength = random.choice(["有力", "无力", "中等"])
            pulse_rhythm = random.choice(["规律", "不规律"])
            syndrome = random.choice(self.syndrome_types)
            constitution = random.choice(self.constitution_types)
            herbs = random.sample(self.herbs, k=random.randint(3, 8))
            formulas = random.sample(self.formulas, k=random.randint(1, 3))
            
            # 生成特征描述
            features = []
            if random.random() > 0.5:
                features.append("左寸" + random.choice(["强", "弱", "正常"]))
            if random.random() > 0.5:
                features.append("左关" + random.choice(["强", "弱", "正常"]))
            if random.random() > 0.5:
                features.append("左尺" + random.choice(["强", "弱", "正常"]))
            if random.random() > 0.5:
                features.append("右寸" + random.choice(["强", "弱", "正常"]))
            if random.random() > 0.5:
                features.append("右关" + random.choice(["强", "弱", "正常"]))
            if random.random() > 0.5:
                features.append("右尺" + random.choice(["强", "弱", "正常"]))
            
            entry = {
                "id": f"pulse_{_:04d}",
                "pulse_type": pulse_type,
                "pulse_strength": pulse_strength,
                "pulse_rhythm": pulse_rhythm,
                "syndrome": syndrome,
                "constitution": constitution,
                "herbs": herbs,
                "formulas": formulas,
                "features": features,
                "description": f"该患者脉象为{pulse_type}，{pulse_strength}，节律{pulse_rhythm}，辨证为{syndrome}。",
                "timestamp": datetime.datetime.now().isoformat()
            }
            dataset.append(entry)
        
        return dataset

    def generate_face_dataset(self) -> List[Dict[str, Any]]:
        """
        生成面诊数据集
        :return: 面诊数据集
        """
        dataset = []
        for _ in range(self.sample_size):
            face_color = random.choice(self.face_color_types)
            pulse_type = random.choice(self.pulse_types)
            syndrome = random.choice(self.syndrome_types)
            constitution = random.choice(self.constitution_types)
            herbs = random.sample(self.herbs, k=random.randint(3, 8))
            formulas = random.sample(self.formulas, k=random.randint(1, 3))
            
            # 生成特征描述
            features = []
            if random.random() > 0.5:
                features.append("眼" + random.choice(["明亮", "混浊", "充血", "黯淡"]))
            if random.random() > 0.5:
                features.append("唇" + random.choice(["红润", "苍白", "暗紫", "干裂"]))
            if random.random() > 0.5:
                features.append("鼻" + random.choice(["红", "白", "正常"]))
            if random.random() > 0.5:
                features.append("面部" + random.choice(["水肿", "消瘦", "正常"]))
            
            entry = {
                "id": f"face_{_:04d}",
                "face_color": face_color,
                "pulse_type": pulse_type,
                "syndrome": syndrome,
                "constitution": constitution,
                "herbs": herbs,
                "formulas": formulas,
                "features": features,
                "description": f"该患者{face_color}，脉象为{pulse_type}，辨证为{syndrome}。",
                "timestamp": datetime.datetime.now().isoformat()
            }
            dataset.append(entry)
        
        return dataset

    def generate_and_save(self):
        """生成并保存所有数据集"""
        
        print(f"正在生成舌诊数据集 ({self.sample_size} 条记录)...")
        tongue_dataset = self.generate_tongue_dataset()
        tongue_path = os.path.join(self.output_dir, "tongue_dataset.json")
        with open(tongue_path, 'w', encoding='utf-8') as f:
            json.dump(tongue_dataset, f, ensure_ascii=False, indent=2)
        print(f"舌诊数据集已保存至: {tongue_path}")
        
        print(f"正在生成脉诊数据集 ({self.sample_size} 条记录)...")
        pulse_dataset = self.generate_pulse_dataset()
        pulse_path = os.path.join(self.output_dir, "pulse_dataset.json")
        with open(pulse_path, 'w', encoding='utf-8') as f:
            json.dump(pulse_dataset, f, ensure_ascii=False, indent=2)
        print(f"脉诊数据集已保存至: {pulse_path}")
        
        print(f"正在生成面诊数据集 ({self.sample_size} 条记录)...")
        face_dataset = self.generate_face_dataset()
        face_path = os.path.join(self.output_dir, "face_dataset.json")
        with open(face_path, 'w', encoding='utf-8') as f:
            json.dump(face_dataset, f, ensure_ascii=False, indent=2)
        print(f"面诊数据集已保存至: {face_path}")
        
        # 生成索引文件
        index = {
            "datasets": [
                {"name": "舌诊数据集", "path": "tongue_dataset.json", "count": len(tongue_dataset)},
                {"name": "脉诊数据集", "path": "pulse_dataset.json", "count": len(pulse_dataset)},
                {"name": "面诊数据集", "path": "face_dataset.json", "count": len(face_dataset)}
            ],
            "total_samples": len(tongue_dataset) + len(pulse_dataset) + len(face_dataset),
            "creation_time": datetime.datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        index_path = os.path.join(self.output_dir, "index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        print(f"索引文件已保存至: {index_path}")
        print(f"共生成 {index['total_samples']} 条数据记录")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="索克生活TCM数据集生成工具")
    parser.add_argument("-o", "--output", type=str, 
                        default="/Users/songxu/Developer/suoke_life/assets/datasets/tcm",
                        help="数据集输出目录")
    parser.add_argument("-n", "--num-samples", type=int, default=100,
                        help="每个数据集的样本数量")
    parser.add_argument("-s", "--seed", type=int, default=None,
                        help="随机种子")
    
    args = parser.parse_args()
    
    # 创建生成器并生成数据集
    generator = TCMDatasetGenerator(
        output_dir=args.output,
        sample_size=args.num_samples,
        random_seed=args.seed
    )
    
    generator.generate_and_save()


if __name__ == "__main__":
    main() 