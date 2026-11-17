# openmv-ili9341
ILI9341 display controller for OpenMV MicroPython [SPIDisplay](https://docs.openmv.io/latest/library/omv.display.spidisplay.html) class.


## Example usage
```python
import csi
import time
import display
from ili9341 import ILI9341Controller

csi0 = csi.CSI()
csi0.reset()
csi0.pixformat(csi.RGB565)
csi0.framesize(csi.QVGA) # 320x200 on AE3, 320x240 on H7
csi0.snapshot(time=2000)

lcd = display.SPIDisplay(width=320, height=240, refresh=20, controller=ILI9341Controller())
clock = time.clock()

while True:
    clock.tick()
    img = csi0.snapshot()
    img.draw_cross((img.width()//2, img.height()//2), color=(255, 0, 0)) # example image manipulation
    lcd.write(img, y=(lcd.height()-img.height())//2)
    print(clock.fps())
```

Connect the pins according to the [LCD Shield pinout](https://docs.openmv.io/latest/openmvcam/shields/touch-lcd-shield.html#pinout), except unused P1 (LCD TE).

If the display is connected to the backside header of an __AE3__ cam:
- connect LED (Backlight) and Reset pins to 3.3V
- connect DC (RS) pin to P1 (MISO) and add `miso_as_rs=True` to the `SPIDisplay` constructor, because the default RS pin is only available at the B2B header of the AE3 cam.

