"""
传感器管理API
提供传感器连接、数据采集和管理功能
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Set
import asyncio
import json
import logging
from datetime import datetime
import uuid

from ..internal.sensor_interface import (
    SensorManager,
    SensorConfig,
    SensorConnectionType,
    SensorStatus,
    DataQuality,
    PREDEFINED_SENSOR_CONFIGS,
    create_sensor_manager_with_defaults
)

logger = logging.getLogger(__name__)

# Pydantic模型定义
class SensorConfigRequest(BaseModel):
    """传感器配置请求模型"""
    device_id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    connection_type: str = Field(..., description="连接类型")
    connection_params: Dict[str, Any] = Field(..., description="连接参数")
    sampling_rate: int = Field(1000, description="采样率")
    data_format: str = Field("ascii_csv", description="数据格式")
    calibration_params: Dict[str, Any] = Field(default_factory=dict, description="校准参数")
    quality_thresholds: Dict[str, float] = Field(default_factory=dict, description="质量阈值")

class SensorStatusResponse(BaseModel):
    """传感器状态响应模型"""
    device_id: str
    device_name: str
    status: str
    connection_type: str
    sampling_rate: int
    is_streaming: bool
    last_data_time: Optional[datetime] = None
    data_quality: Optional[str] = None

class DataStreamConfig(BaseModel):
    """数据流配置模型"""
    sensors: List[str] = Field(..., description="传感器ID列表")
    duration: Optional[int] = Field(None, description="采集时长(秒)")
    buffer_size: int = Field(1000, description="缓冲区大小")
    quality_filter: bool = Field(True, description="是否启用质量过滤")

class CalibrationRequest(BaseModel):
    """校准请求模型"""
    sensor_id: str = Field(..., description="传感器ID")
    calibration_type: str = Field("standard", description="校准类型")
    reference_values: Optional[Dict[str, float]] = Field(None, description="参考值")

# 创建FastAPI应用
app = FastAPI(
    title="传感器管理API",
    description="脉象传感器数据采集和管理系统",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
sensor_manager = create_sensor_manager_with_defaults()
active_websockets: Set[WebSocket] = set()
data_streams: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("传感器管理API服务启动")
    
    # 添加数据处理器
    sensor_manager.add_data_handler(broadcast_sensor_data)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("传感器管理API服务关闭")
    
    # 断开所有传感器
    await sensor_manager.disconnect_all()

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "sensor-management-api",
        "version": "1.0.0",
        "sensors_count": len(sensor_manager.sensors)
    }

@app.get("/api/v1/sensors", response_model=List[SensorStatusResponse])
async def list_sensors():
    """获取所有传感器列表"""
    try:
        sensor_status = sensor_manager.get_sensor_status()
        
        sensors = []
        for device_id, status_info in sensor_status.items():
            sensors.append(SensorStatusResponse(
                device_id=device_id,
                device_name=status_info["device_name"],
                status=status_info["status"],
                connection_type=status_info["connection_type"],
                sampling_rate=status_info["sampling_rate"],
                is_streaming=status_info["is_streaming"]
            ))
        
        return sensors
        
    except Exception as e:
        logger.error(f"获取传感器列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取传感器列表失败: {str(e)}")

@app.post("/api/v1/sensors")
async def register_sensor(config_request: SensorConfigRequest):
    """注册新传感器"""
    try:
        # 转换连接类型
        connection_type = SensorConnectionType(config_request.connection_type)
        
        # 创建传感器配置
        sensor_config = SensorConfig(
            device_id=config_request.device_id,
            device_name=config_request.device_name,
            connection_type=connection_type,
            connection_params=config_request.connection_params,
            sampling_rate=config_request.sampling_rate,
            data_format=config_request.data_format,
            calibration_params=config_request.calibration_params,
            quality_thresholds=config_request.quality_thresholds or {
                'min_value': 0.1,
                'max_value': 10.0,
                'excellent_threshold': 0.8,
                'good_threshold': 0.6
            }
        )
        
        # 注册传感器
        success = sensor_manager.register_sensor(sensor_config)
        
        if success:
            return {
                "status": "success",
                "message": f"传感器 {config_request.device_id} 注册成功",
                "device_id": config_request.device_id
            }
        else:
            raise HTTPException(status_code=400, detail="传感器注册失败")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的连接类型: {str(e)}")
    except Exception as e:
        logger.error(f"注册传感器失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册传感器失败: {str(e)}")

@app.delete("/api/v1/sensors/{device_id}")
async def unregister_sensor(device_id: str):
    """注销传感器"""
    try:
        success = sensor_manager.unregister_sensor(device_id)
        
        if success:
            return {
                "status": "success",
                "message": f"传感器 {device_id} 注销成功"
            }
        else:
            raise HTTPException(status_code=404, detail="传感器不存在")
            
    except Exception as e:
        logger.error(f"注销传感器失败: {e}")
        raise HTTPException(status_code=500, detail=f"注销传感器失败: {str(e)}")

@app.post("/api/v1/sensors/{device_id}/connect")
async def connect_sensor(device_id: str):
    """连接传感器"""
    try:
        if device_id not in sensor_manager.sensors:
            raise HTTPException(status_code=404, detail="传感器不存在")
        
        sensor = sensor_manager.sensors[device_id]
        success = await sensor.connect()
        
        if success:
            return {
                "status": "success",
                "message": f"传感器 {device_id} 连接成功",
                "sensor_status": sensor.status.value
            }
        else:
            raise HTTPException(status_code=400, detail="传感器连接失败")
            
    except Exception as e:
        logger.error(f"连接传感器失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接传感器失败: {str(e)}")

@app.post("/api/v1/sensors/{device_id}/disconnect")
async def disconnect_sensor(device_id: str):
    """断开传感器连接"""
    try:
        if device_id not in sensor_manager.sensors:
            raise HTTPException(status_code=404, detail="传感器不存在")
        
        sensor = sensor_manager.sensors[device_id]
        success = await sensor.disconnect()
        
        if success:
            return {
                "status": "success",
                "message": f"传感器 {device_id} 断开连接成功",
                "sensor_status": sensor.status.value
            }
        else:
            raise HTTPException(status_code=400, detail="传感器断开连接失败")
            
    except Exception as e:
        logger.error(f"断开传感器连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"断开传感器连接失败: {str(e)}")

@app.post("/api/v1/sensors/connect-all")
async def connect_all_sensors():
    """连接所有传感器"""
    try:
        results = await sensor_manager.connect_all()
        
        return {
            "status": "completed",
            "results": results,
            "summary": {
                "total": len(results),
                "successful": sum(1 for success in results.values() if success),
                "failed": sum(1 for success in results.values() if not success)
            }
        }
        
    except Exception as e:
        logger.error(f"连接所有传感器失败: {e}")
        raise HTTPException(status_code=500, detail=f"连接所有传感器失败: {str(e)}")

@app.post("/api/v1/sensors/disconnect-all")
async def disconnect_all_sensors():
    """断开所有传感器连接"""
    try:
        results = await sensor_manager.disconnect_all()
        
        return {
            "status": "completed",
            "results": results,
            "summary": {
                "total": len(results),
                "successful": sum(1 for success in results.values() if success),
                "failed": sum(1 for success in results.values() if not success)
            }
        }
        
    except Exception as e:
        logger.error(f"断开所有传感器连接失败: {e}")
        raise HTTPException(status_code=500, detail=f"断开所有传感器连接失败: {str(e)}")

@app.post("/api/v1/sensors/{device_id}/calibrate")
async def calibrate_sensor(device_id: str, request: CalibrationRequest):
    """校准传感器"""
    try:
        if device_id not in sensor_manager.sensors:
            raise HTTPException(status_code=404, detail="传感器不存在")
        
        sensor = sensor_manager.sensors[device_id]
        
        # 更新校准参数
        if request.reference_values:
            sensor.config.calibration_params.update(request.reference_values)
        
        success = await sensor.calibrate()
        
        if success:
            return {
                "status": "success",
                "message": f"传感器 {device_id} 校准成功",
                "calibration_type": request.calibration_type,
                "sensor_status": sensor.status.value
            }
        else:
            raise HTTPException(status_code=400, detail="传感器校准失败")
            
    except Exception as e:
        logger.error(f"校准传感器失败: {e}")
        raise HTTPException(status_code=500, detail=f"校准传感器失败: {str(e)}")

@app.post("/api/v1/data-stream/start")
async def start_data_stream(config: DataStreamConfig, background_tasks: BackgroundTasks):
    """开始数据流采集"""
    try:
        stream_id = str(uuid.uuid4())
        
        # 验证传感器
        for sensor_id in config.sensors:
            if sensor_id not in sensor_manager.sensors:
                raise HTTPException(status_code=404, detail=f"传感器 {sensor_id} 不存在")
        
        # 创建数据流配置
        stream_config = {
            "stream_id": stream_id,
            "sensors": config.sensors,
            "duration": config.duration,
            "buffer_size": config.buffer_size,
            "quality_filter": config.quality_filter,
            "start_time": datetime.now(),
            "status": "starting",
            "data_count": 0
        }
        
        data_streams[stream_id] = stream_config
        
        # 启动数据流
        background_tasks.add_task(manage_data_stream, stream_id, config)
        
        return {
            "status": "success",
            "stream_id": stream_id,
            "message": "数据流启动中...",
            "config": stream_config
        }
        
    except Exception as e:
        logger.error(f"启动数据流失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动数据流失败: {str(e)}")

@app.post("/api/v1/data-stream/{stream_id}/stop")
async def stop_data_stream(stream_id: str):
    """停止数据流采集"""
    try:
        if stream_id not in data_streams:
            raise HTTPException(status_code=404, detail="数据流不存在")
        
        stream_config = data_streams[stream_id]
        stream_config["status"] = "stopping"
        
        # 停止相关传感器的数据流
        for sensor_id in stream_config["sensors"]:
            if sensor_id in sensor_manager.sensors:
                sensor = sensor_manager.sensors[sensor_id]
                await sensor.stop_streaming()
        
        stream_config["status"] = "stopped"
        stream_config["end_time"] = datetime.now()
        
        return {
            "status": "success",
            "stream_id": stream_id,
            "message": "数据流已停止",
            "summary": {
                "duration": (stream_config["end_time"] - stream_config["start_time"]).total_seconds(),
                "data_count": stream_config["data_count"]
            }
        }
        
    except Exception as e:
        logger.error(f"停止数据流失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止数据流失败: {str(e)}")

@app.get("/api/v1/data-stream/{stream_id}/status")
async def get_data_stream_status(stream_id: str):
    """获取数据流状态"""
    try:
        if stream_id not in data_streams:
            raise HTTPException(status_code=404, detail="数据流不存在")
        
        stream_config = data_streams[stream_id]
        
        # 计算运行时间
        if stream_config["status"] in ["running", "starting"]:
            runtime = (datetime.now() - stream_config["start_time"]).total_seconds()
        else:
            runtime = (stream_config.get("end_time", datetime.now()) - stream_config["start_time"]).total_seconds()
        
        return {
            "stream_id": stream_id,
            "status": stream_config["status"],
            "runtime_seconds": runtime,
            "data_count": stream_config["data_count"],
            "sensors": stream_config["sensors"],
            "start_time": stream_config["start_time"],
            "end_time": stream_config.get("end_time")
        }
        
    except Exception as e:
        logger.error(f"获取数据流状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据流状态失败: {str(e)}")

@app.get("/api/v1/predefined-configs")
async def get_predefined_configs():
    """获取预定义的传感器配置"""
    try:
        configs = {}
        for config_id, config in PREDEFINED_SENSOR_CONFIGS.items():
            configs[config_id] = {
                "device_id": config.device_id,
                "device_name": config.device_name,
                "connection_type": config.connection_type.value,
                "sampling_rate": config.sampling_rate,
                "data_format": config.data_format,
                "description": f"{config.device_name} - {config.connection_type.value}连接"
            }
        
        return {
            "status": "success",
            "configs": configs
        }
        
    except Exception as e:
        logger.error(f"获取预定义配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取预定义配置失败: {str(e)}")

@app.post("/api/v1/sensors/load-predefined/{config_id}")
async def load_predefined_config(config_id: str):
    """加载预定义传感器配置"""
    try:
        if config_id not in PREDEFINED_SENSOR_CONFIGS:
            raise HTTPException(status_code=404, detail="预定义配置不存在")
        
        config = PREDEFINED_SENSOR_CONFIGS[config_id]
        success = sensor_manager.register_sensor(config)
        
        if success:
            return {
                "status": "success",
                "message": f"预定义配置 {config_id} 加载成功",
                "device_id": config.device_id,
                "device_name": config.device_name
            }
        else:
            raise HTTPException(status_code=400, detail="加载预定义配置失败")
            
    except Exception as e:
        logger.error(f"加载预定义配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"加载预定义配置失败: {str(e)}")

@app.websocket("/ws/sensor-data")
async def websocket_sensor_data(websocket: WebSocket):
    """WebSocket传感器数据流"""
    await websocket.accept()
    active_websockets.add(websocket)
    
    try:
        while True:
            # 保持连接活跃
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        logger.info("WebSocket客户端断开连接")
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)

async def manage_data_stream(stream_id: str, config: DataStreamConfig):
    """管理数据流采集"""
    try:
        stream_config = data_streams[stream_id]
        
        # 启动传感器数据流
        for sensor_id in config.sensors:
            sensor = sensor_manager.sensors[sensor_id]
            await sensor.start_streaming()
        
        stream_config["status"] = "running"
        
        # 如果设置了持续时间，等待指定时间后自动停止
        if config.duration:
            await asyncio.sleep(config.duration)
            
            # 停止传感器数据流
            for sensor_id in config.sensors:
                sensor = sensor_manager.sensors[sensor_id]
                await sensor.stop_streaming()
            
            stream_config["status"] = "completed"
            stream_config["end_time"] = datetime.now()
        
    except Exception as e:
        logger.error(f"管理数据流失败 {stream_id}: {e}")
        if stream_id in data_streams:
            data_streams[stream_id]["status"] = "error"
            data_streams[stream_id]["error"] = str(e)

def broadcast_sensor_data(reading):
    """广播传感器数据到WebSocket客户端"""
    if not active_websockets:
        return
    
    try:
        # 更新数据流计数
        for stream_id, stream_config in data_streams.items():
            if (stream_config["status"] == "running" and 
                reading.device_id in stream_config["sensors"]):
                stream_config["data_count"] += 1
        
        # 准备广播数据
        data = {
            "type": "sensor_data",
            "timestamp": datetime.now().isoformat(),
            "device_id": reading.device_id,
            "sensor_type": reading.sensor_type,
            "value": reading.raw_value if isinstance(reading.raw_value, (int, float)) else list(reading.raw_value),
            "quality": reading.quality.value,
            "metadata": reading.metadata or {}
        }
        
        # 广播到所有活跃的WebSocket连接
        disconnected_websockets = set()
        for websocket in active_websockets:
            try:
                asyncio.create_task(websocket.send_text(json.dumps(data)))
            except Exception as e:
                logger.warning(f"WebSocket发送失败: {e}")
                disconnected_websockets.add(websocket)
        
        # 移除断开的连接
        active_websockets -= disconnected_websockets
        
    except Exception as e:
        logger.error(f"广播传感器数据失败: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 