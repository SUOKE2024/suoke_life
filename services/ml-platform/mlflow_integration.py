"""
MLflow AI/ML平台集成
用于索克生活项目的模型管理、实验跟踪和模型部署
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
import os
import tempfile
import pickle
import joblib

import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.tensorflow
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature
from mlflow.store.artifact.runs_artifact_repo import RunsArtifactRepository
import pandas as pd
import numpy as np
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str
    model_version: str
    model_type: str  # sklearn, pytorch, tensorflow, custom
    description: str
    tags: Dict[str, str] = None
    parameters: Dict[str, Any] = None

@dataclass
class ExperimentConfig:
    """实验配置"""
    experiment_name: str
    description: str
    tags: Dict[str, str] = None

@dataclass
class ModelMetrics:
    """模型指标"""
    accuracy: float = None
    precision: float = None
    recall: float = None
    f1_score: float = None
    auc: float = None
    rmse: float = None
    mae: float = None
    custom_metrics: Dict[str, float] = None

class SuokeMLflowClient:
    """索克生活MLflow客户端"""
    
    def __init__(self, 
                 tracking_uri: str = "http://mlflow:5000",
                 artifact_uri: str = "s3://mlflow-artifacts",
                 registry_uri: str = None):
        self.tracking_uri = tracking_uri
        self.artifact_uri = artifact_uri
        self.registry_uri = registry_uri or tracking_uri
        
        # 设置MLflow配置
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_registry_uri(self.registry_uri)
        
        self.client = MlflowClient(tracking_uri=self.tracking_uri)
        
        # 预定义实验
        self.experiments = {
            "health_diagnosis": "健康诊断模型实验",
            "tcm_constitution": "中医体质分析实验", 
            "symptom_classification": "症状分类实验",
            "health_prediction": "健康预测实验",
            "agent_recommendation": "智能体推荐实验"
        }
        
        logger.info("MLflow客户端初始化完成",
                   tracking_uri=self.tracking_uri,
                   registry_uri=self.registry_uri)
    
    async def initialize_experiments(self):
        """初始化实验"""
        for exp_name, description in self.experiments.items():
            try:
                experiment = mlflow.get_experiment_by_name(exp_name)
                if experiment is None:
                    experiment_id = mlflow.create_experiment(
                        name=exp_name,
                        artifact_location=f"{self.artifact_uri}/{exp_name}",
                        tags={"project": "suoke_life", "type": "health_ai"}
                    )
                    logger.info("创建实验成功", 
                               experiment_name=exp_name,
                               experiment_id=experiment_id)
                else:
                    logger.info("实验已存在", 
                               experiment_name=exp_name,
                               experiment_id=experiment.experiment_id)
            except Exception as e:
                logger.error("创建实验失败", 
                           experiment_name=exp_name,
                           error=str(e))
    
    def start_run(self, 
                  experiment_name: str,
                  run_name: str = None,
                  tags: Dict[str, str] = None) -> str:
        """开始实验运行"""
        mlflow.set_experiment(experiment_name)
        
        run_tags = {
            "project": "suoke_life",
            "timestamp": datetime.utcnow().isoformat()
        }
        if tags:
            run_tags.update(tags)
        
        run = mlflow.start_run(run_name=run_name, tags=run_tags)
        
        logger.info("开始实验运行",
                   experiment_name=experiment_name,
                   run_id=run.info.run_id,
                   run_name=run_name)
        
        return run.info.run_id
    
    def log_parameters(self, parameters: Dict[str, Any]):
        """记录参数"""
        for key, value in parameters.items():
            mlflow.log_param(key, value)
        
        logger.debug("记录参数", parameters=parameters)
    
    def log_metrics(self, metrics: ModelMetrics, step: int = None):
        """记录指标"""
        metrics_dict = {}
        
        # 标准指标
        if metrics.accuracy is not None:
            metrics_dict["accuracy"] = metrics.accuracy
        if metrics.precision is not None:
            metrics_dict["precision"] = metrics.precision
        if metrics.recall is not None:
            metrics_dict["recall"] = metrics.recall
        if metrics.f1_score is not None:
            metrics_dict["f1_score"] = metrics.f1_score
        if metrics.auc is not None:
            metrics_dict["auc"] = metrics.auc
        if metrics.rmse is not None:
            metrics_dict["rmse"] = metrics.rmse
        if metrics.mae is not None:
            metrics_dict["mae"] = metrics.mae
        
        # 自定义指标
        if metrics.custom_metrics:
            metrics_dict.update(metrics.custom_metrics)
        
        for key, value in metrics_dict.items():
            mlflow.log_metric(key, value, step=step)
        
        logger.debug("记录指标", metrics=metrics_dict, step=step)
    
    def log_model(self, 
                  model: Any,
                  model_name: str,
                  model_type: str = "sklearn",
                  signature: Any = None,
                  input_example: Any = None,
                  conda_env: str = None,
                  pip_requirements: List[str] = None) -> str:
        """记录模型"""
        try:
            if model_type == "sklearn":
                model_info = mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path=model_name,
                    signature=signature,
                    input_example=input_example,
                    conda_env=conda_env,
                    pip_requirements=pip_requirements
                )
            elif model_type == "pytorch":
                model_info = mlflow.pytorch.log_model(
                    pytorch_model=model,
                    artifact_path=model_name,
                    signature=signature,
                    input_example=input_example,
                    conda_env=conda_env,
                    pip_requirements=pip_requirements
                )
            elif model_type == "tensorflow":
                model_info = mlflow.tensorflow.log_model(
                    tf_saved_model_dir=model,
                    artifact_path=model_name,
                    signature=signature,
                    input_example=input_example,
                    conda_env=conda_env,
                    pip_requirements=pip_requirements
                )
            else:
                # 自定义模型
                model_info = mlflow.pyfunc.log_model(
                    artifact_path=model_name,
                    python_model=model,
                    signature=signature,
                    input_example=input_example,
                    conda_env=conda_env,
                    pip_requirements=pip_requirements
                )
            
            logger.info("模型记录成功",
                       model_name=model_name,
                       model_type=model_type,
                       model_uri=model_info.model_uri)
            
            return model_info.model_uri
            
        except Exception as e:
            logger.error("模型记录失败",
                        model_name=model_name,
                        model_type=model_type,
                        error=str(e))
            raise
    
    def register_model(self, 
                      model_uri: str,
                      model_name: str,
                      description: str = None,
                      tags: Dict[str, str] = None) -> str:
        """注册模型到模型注册表"""
        try:
            model_version = mlflow.register_model(
                model_uri=model_uri,
                name=model_name,
                tags=tags
            )
            
            if description:
                self.client.update_model_version(
                    name=model_name,
                    version=model_version.version,
                    description=description
                )
            
            logger.info("模型注册成功",
                       model_name=model_name,
                       version=model_version.version,
                       model_uri=model_uri)
            
            return model_version.version
            
        except Exception as e:
            logger.error("模型注册失败",
                        model_name=model_name,
                        model_uri=model_uri,
                        error=str(e))
            raise
    
    def transition_model_stage(self, 
                              model_name: str,
                              version: str,
                              stage: str,
                              archive_existing_versions: bool = False) -> bool:
        """转换模型阶段"""
        try:
            self.client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage,
                archive_existing_versions=archive_existing_versions
            )
            
            logger.info("模型阶段转换成功",
                       model_name=model_name,
                       version=version,
                       stage=stage)
            
            return True
            
        except Exception as e:
            logger.error("模型阶段转换失败",
                        model_name=model_name,
                        version=version,
                        stage=stage,
                        error=str(e))
            return False
    
    def load_model(self, 
                   model_name: str,
                   version: str = None,
                   stage: str = None) -> Any:
        """加载模型"""
        try:
            if version:
                model_uri = f"models:/{model_name}/{version}"
            elif stage:
                model_uri = f"models:/{model_name}/{stage}"
            else:
                model_uri = f"models:/{model_name}/latest"
            
            model = mlflow.pyfunc.load_model(model_uri)
            
            logger.info("模型加载成功",
                       model_name=model_name,
                       version=version,
                       stage=stage,
                       model_uri=model_uri)
            
            return model
            
        except Exception as e:
            logger.error("模型加载失败",
                        model_name=model_name,
                        version=version,
                        stage=stage,
                        error=str(e))
            raise
    
    def get_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """获取模型版本列表"""
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            
            version_info = []
            for version in versions:
                version_info.append({
                    "version": version.version,
                    "stage": version.current_stage,
                    "status": version.status,
                    "creation_timestamp": version.creation_timestamp,
                    "last_updated_timestamp": version.last_updated_timestamp,
                    "description": version.description,
                    "tags": version.tags,
                    "run_id": version.run_id
                })
            
            return version_info
            
        except Exception as e:
            logger.error("获取模型版本失败",
                        model_name=model_name,
                        error=str(e))
            return []
    
    def end_run(self, status: str = "FINISHED"):
        """结束实验运行"""
        mlflow.end_run(status=status)
        logger.debug("实验运行结束", status=status)

class HealthDiagnosisModel:
    """健康诊断模型示例"""
    
    def __init__(self, mlflow_client: SuokeMLflowClient):
        self.mlflow_client = mlflow_client
        self.model = None
        self.model_name = "health_diagnosis_model"
    
    def train(self, 
              X_train: pd.DataFrame,
              y_train: pd.Series,
              X_val: pd.DataFrame = None,
              y_val: pd.Series = None,
              model_params: Dict[str, Any] = None) -> str:
        """训练模型"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        # 开始MLflow运行
        run_id = self.mlflow_client.start_run(
            experiment_name="health_diagnosis",
            run_name=f"health_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tags={"model_type": "random_forest", "task": "classification"}
        )
        
        try:
            # 默认参数
            default_params = {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "min_samples_leaf": 2,
                "random_state": 42
            }
            
            if model_params:
                default_params.update(model_params)
            
            # 记录参数
            self.mlflow_client.log_parameters(default_params)
            self.mlflow_client.log_parameters({
                "train_samples": len(X_train),
                "features": len(X_train.columns),
                "classes": len(y_train.unique())
            })
            
            # 训练模型
            self.model = RandomForestClassifier(**default_params)
            self.model.fit(X_train, y_train)
            
            # 验证模型
            if X_val is not None and y_val is not None:
                y_pred = self.model.predict(X_val)
                
                metrics = ModelMetrics(
                    accuracy=accuracy_score(y_val, y_pred),
                    precision=precision_score(y_val, y_pred, average='weighted'),
                    recall=recall_score(y_val, y_pred, average='weighted'),
                    f1_score=f1_score(y_val, y_pred, average='weighted')
                )
                
                self.mlflow_client.log_metrics(metrics)
            
            # 记录模型
            signature = infer_signature(X_train, self.model.predict(X_train))
            model_uri = self.mlflow_client.log_model(
                model=self.model,
                model_name=self.model_name,
                model_type="sklearn",
                signature=signature,
                input_example=X_train.head(5),
                pip_requirements=["scikit-learn", "pandas", "numpy"]
            )
            
            # 注册模型
            version = self.mlflow_client.register_model(
                model_uri=model_uri,
                model_name=self.model_name,
                description="健康诊断随机森林模型"
            )
            
            self.mlflow_client.end_run("FINISHED")
            
            logger.info("健康诊断模型训练完成",
                       run_id=run_id,
                       model_version=version)
            
            return version
            
        except Exception as e:
            self.mlflow_client.end_run("FAILED")
            logger.error("健康诊断模型训练失败", error=str(e))
            raise
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if self.model is None:
            # 加载最新的生产模型
            self.model = self.mlflow_client.load_model(
                model_name=self.model_name,
                stage="Production"
            )
        
        return self.model.predict(X)

class TCMConstitutionModel:
    """中医体质分析模型"""
    
    def __init__(self, mlflow_client: SuokeMLflowClient):
        self.mlflow_client = mlflow_client
        self.model = None
        self.model_name = "tcm_constitution_model"
    
    def train(self, 
              constitution_data: pd.DataFrame,
              model_params: Dict[str, Any] = None) -> str:
        """训练中医体质分析模型"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import silhouette_score
        
        # 开始MLflow运行
        run_id = self.mlflow_client.start_run(
            experiment_name="tcm_constitution",
            run_name=f"tcm_constitution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tags={"model_type": "kmeans", "task": "clustering"}
        )
        
        try:
            # 数据预处理
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(constitution_data)
            
            # 默认参数
            default_params = {
                "n_clusters": 9,  # 九种体质
                "random_state": 42,
                "max_iter": 300,
                "n_init": 10
            }
            
            if model_params:
                default_params.update(model_params)
            
            # 记录参数
            self.mlflow_client.log_parameters(default_params)
            self.mlflow_client.log_parameters({
                "samples": len(constitution_data),
                "features": len(constitution_data.columns)
            })
            
            # 训练模型
            self.model = KMeans(**default_params)
            clusters = self.model.fit_predict(X_scaled)
            
            # 计算指标
            silhouette_avg = silhouette_score(X_scaled, clusters)
            inertia = self.model.inertia_
            
            metrics = ModelMetrics(
                custom_metrics={
                    "silhouette_score": silhouette_avg,
                    "inertia": inertia,
                    "n_clusters": default_params["n_clusters"]
                }
            )
            
            self.mlflow_client.log_metrics(metrics)
            
            # 保存预处理器和模型
            with tempfile.TemporaryDirectory() as temp_dir:
                scaler_path = os.path.join(temp_dir, "scaler.pkl")
                model_path = os.path.join(temp_dir, "model.pkl")
                
                joblib.dump(scaler, scaler_path)
                joblib.dump(self.model, model_path)
                
                mlflow.log_artifact(scaler_path, "preprocessor")
                mlflow.log_artifact(model_path, "model")
            
            # 记录模型
            model_uri = self.mlflow_client.log_model(
                model={"scaler": scaler, "model": self.model},
                model_name=self.model_name,
                model_type="sklearn",
                pip_requirements=["scikit-learn", "pandas", "numpy", "joblib"]
            )
            
            # 注册模型
            version = self.mlflow_client.register_model(
                model_uri=model_uri,
                model_name=self.model_name,
                description="中医体质分析聚类模型"
            )
            
            self.mlflow_client.end_run("FINISHED")
            
            logger.info("中医体质模型训练完成",
                       run_id=run_id,
                       model_version=version,
                       silhouette_score=silhouette_avg)
            
            return version
            
        except Exception as e:
            self.mlflow_client.end_run("FAILED")
            logger.error("中医体质模型训练失败", error=str(e))
            raise

# 模型服务部署
class ModelServingService:
    """模型服务部署"""
    
    def __init__(self, mlflow_client: SuokeMLflowClient):
        self.mlflow_client = mlflow_client
        self.deployed_models: Dict[str, Any] = {}
    
    async def deploy_model(self, 
                          model_name: str,
                          version: str = None,
                          stage: str = "Production",
                          port: int = 5001) -> bool:
        """部署模型服务"""
        try:
            # 加载模型
            model = self.mlflow_client.load_model(
                model_name=model_name,
                version=version,
                stage=stage
            )
            
            # 启动模型服务
            # 这里可以集成到Kubernetes或其他容器编排平台
            self.deployed_models[model_name] = {
                "model": model,
                "version": version,
                "stage": stage,
                "port": port,
                "status": "running"
            }
            
            logger.info("模型部署成功",
                       model_name=model_name,
                       version=version,
                       stage=stage,
                       port=port)
            
            return True
            
        except Exception as e:
            logger.error("模型部署失败",
                        model_name=model_name,
                        error=str(e))
            return False
    
    async def predict(self, 
                     model_name: str,
                     input_data: pd.DataFrame) -> Dict[str, Any]:
        """模型预测"""
        if model_name not in self.deployed_models:
            raise ValueError(f"模型 {model_name} 未部署")
        
        try:
            model_info = self.deployed_models[model_name]
            model = model_info["model"]
            
            predictions = model.predict(input_data)
            
            return {
                "model_name": model_name,
                "version": model_info["version"],
                "predictions": predictions.tolist(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("模型预测失败",
                        model_name=model_name,
                        error=str(e))
            raise

# 使用示例
async def example_usage():
    """使用示例"""
    # 初始化MLflow客户端
    mlflow_client = SuokeMLflowClient(
        tracking_uri="http://localhost:5000",
        artifact_uri="./mlruns"
    )
    
    # 初始化实验
    await mlflow_client.initialize_experiments()
    
    # 训练健康诊断模型
    health_model = HealthDiagnosisModel(mlflow_client)
    
    # 模拟训练数据
    X_train = pd.DataFrame({
        "age": np.random.randint(20, 80, 1000),
        "heart_rate": np.random.randint(60, 100, 1000),
        "blood_pressure_sys": np.random.randint(90, 140, 1000),
        "blood_pressure_dia": np.random.randint(60, 90, 1000)
    })
    y_train = pd.Series(np.random.choice(["healthy", "at_risk", "unhealthy"], 1000))
    
    # 训练模型
    version = health_model.train(X_train, y_train)
    
    # 转换到生产阶段
    mlflow_client.transition_model_stage(
        model_name="health_diagnosis_model",
        version=version,
        stage="Production"
    )
    
    # 部署模型服务
    serving_service = ModelServingService(mlflow_client)
    await serving_service.deploy_model("health_diagnosis_model")
    
    # 模型预测
    test_data = pd.DataFrame({
        "age": [35],
        "heart_rate": [75],
        "blood_pressure_sys": [120],
        "blood_pressure_dia": [80]
    })
    
    result = await serving_service.predict("health_diagnosis_model", test_data)
    logger.info("预测结果", result=result)

if __name__ == "__main__":
    asyncio.run(example_usage()) 