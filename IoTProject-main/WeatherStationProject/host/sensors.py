import w1thermsensor
import adafruit_bme280.advanced as adafruit_bme280
import board
import busio
    

def getData():
    sensor = w1thermsensor.W1ThermSensor()
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    bme280.overscan_humidity = adafruit_bme280.OVERSCAN_X1
    temp = sensor.get_temperature()
    humid = bme280.humidity
    return temp, humid