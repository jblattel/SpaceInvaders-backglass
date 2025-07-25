import board
import busio
import adafruit_mcp230xx.mcp23017 as MCP
from adafruit_mcp230xx.digital_inout import Direction
from adafruit_ht16k33.segments import BigSeg7x4

# Setup MCP23017
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP.MCP23017(i2c, address=0x26)
for pin in range(16):
    mcp.get_pin(pin).direction = Direction.OUTPUT
mcp.gpio = 0xFFFF  # All lights off
#i2c = board.I2C()

#display_upper_left = BigSeg7x4(i2c,address=0x73)
display_upper_right = BigSeg7x4(i2c,address=0x72)
display_lower_right = BigSeg7x4(i2c,address=0x70)
display_lower_left = BigSeg7x4(i2c,address=0x71)

display = BigSeg7x4(i2c, 0x72,0x70,0x71)
display.fill(0)




