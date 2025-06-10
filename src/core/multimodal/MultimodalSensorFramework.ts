import { EventEmitter } from "events";"";"";
, (data: SensorData) => this.handleSensorData(data));";,"";
sensor.on("error, (error: Error) => this.handleSensorError(sensor.getId(), error));";
sensor.on("calibration", (calibration: CalibrationData) => {;})";,"";
this.calibrationManager.updateCalibration(sensor.getId(), calibration);
    );
  }
  /* " *//;"/g"/;
  */"/"/g"/;