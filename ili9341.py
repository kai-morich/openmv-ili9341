"""
ILI9341 controller for OpenMV MicroPython SPIDisplay class

The initialization sequence is adapted from:
https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
"""
from time import sleep
from micropython import const

class ILI9341Controller:
    # Command constants from ILI9341 datasheet
    SWRESET = const(0x01)  # Software reset
    SLPOUT = const(0x11)  # Exit sleep mode
    GAMMASET = const(0x26)  # Gamma set
    DISPLAY_ON = const(0x29)  # Display on
    SET_COLUMN = const(0x2A)  # Column address set
    SET_PAGE = const(0x2B)  # Page address set
    MADCTL = const(0x36)  # Memory access control
    VSCRSADD = const(0x37)  # Vertical scrolling start address
    PIXFMT = const(0x3A)  # COLMOD: Pixel format set
    FRMCTR1 = const(0xB1)  # Frame rate control (In normal mode/full colors)
    DFUNCTR = const(0xB6)  # Display function control
    PWCTR1 = const(0xC0)  # Power control 1
    PWCTR2 = const(0xC1)  # Power control 2
    PWCTRA = const(0xCB)  # Power control A
    PWCTRB = const(0xCF)  # Power control B
    VMCTR1 = const(0xC5)  # VCOM control 1
    VMCTR2 = const(0xC7)  # VCOM control 2
    GMCTRP1 = const(0xE0)  # Positive gamma correction
    GMCTRN1 = const(0xE1)  # Negative gamma correction
    DTCA = const(0xE8)  # Driver timing control A
    DTCB = const(0xEA)  # Driver timing control B
    POSC = const(0xED)  # Power on sequence control
    ENABLE3G = const(0xF2)  # Enable 3 gamma control
    PUMPRC = const(0xF7)  # Pump ratio control

    MIRROR_ROTATE = {  # MADCTL configurations for rotation and mirroring
        (False, 0): 0x80,  # 1000 0000
        (False, 90): 0xE0,  # 1110 0000
        (False, 180): 0x40,  # 0100 0000
        (False, 270): 0x20,  # 0010 0000
        (True, 0): 0xC0,   # 1100 0000
        (True, 90): 0x60,  # 0110 0000
        (True, 180): 0x00,  # 0000 0000
        (True, 270): 0xA0  # 1010 0000
    }

    def __init__(self, mirror=False, rotation=90, gamma=True):
        """To configure the display orientation, use `mirror` and `rotation` here,
        instead of `hflip` and `vmirror` at `SPIDisplay`.
        """
        if (mirror, rotation) not in self.MIRROR_ROTATE:
            raise ValueError('Rotation must be 0, 90, 180 or 270.')
        else:
            self.madtcl = self.MIRROR_ROTATE[mirror, rotation]
        self.gamma = gamma
        self.rotation = rotation

    def init(self, spidisplay):
        """called by `SPIDisplay` during initialization"""
        madtcl = self.madtcl
        if spidisplay.bgr:
            madtcl |= 0x08

        spidisplay.bus_write(self.SWRESET)
        sleep(.15)
        spidisplay.bus_write(self.PWCTRB, b"\x00\xC1\x30")  # Pwr ctrl B
        spidisplay.bus_write(self.POSC, b"\x64\x03\x12\x81")  # Pwr on seq. ctrl
        spidisplay.bus_write(self.DTCA, b"\x85\x00\x78")  # Driver timing ctrl A
        spidisplay.bus_write(self.PWCTRA, b"\x39\x2C\x00\x34\x02")  # Pwr ctrl A
        spidisplay.bus_write(self.PUMPRC, b"\x20")  # Pump ratio control
        spidisplay.bus_write(self.DTCB, b"\x00\x00")  # Driver timing ctrl B
        spidisplay.bus_write(self.PWCTR1, b"\x23")  # Pwr ctrl 1
        spidisplay.bus_write(self.PWCTR2, b"\x10")  # Pwr ctrl 2
        spidisplay.bus_write(self.VMCTR1, b"\x3E\x28")  # VCOM ctrl 1
        spidisplay.bus_write(self.VMCTR2, b"\x86")  # VCOM ctrl 2
        spidisplay.bus_write(self.MADCTL, madtcl)  # Memory access ctrl
        spidisplay.bus_write(self.VSCRSADD, b"\x00")  # Vertical scrolling start address
        spidisplay.bus_write(self.PIXFMT, b"\x55")  # COLMOD: Pixel format
        spidisplay.bus_write(self.FRMCTR1, b"\x00\x18")  # Frame rate ctrl
        spidisplay.bus_write(self.DFUNCTR, b"\x08\x82\x27")
        spidisplay.bus_write(self.ENABLE3G, b"\x00")  # Enable 3 gamma ctrl
        spidisplay.bus_write(self.GAMMASET, b"\x01")  # Gamma curve selected
        if self.gamma:  # Use custom gamma correction values
            spidisplay.bus_write(self.GMCTRP1, b"\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00")
            spidisplay.bus_write(self.GMCTRN1, b"\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F")
        spidisplay.bus_write(self.SLPOUT)  # Exit sleep
        sleep(.15)
        spidisplay.bus_write(self.DISPLAY_ON)
        sleep(.05)

        spidisplay.bus_write(self.MADCTL, madtcl)  # Memory access ctrl
        if self.rotation in (90,270):
            spidisplay.bus_write(SET_COLUMN, b"\x00\x00\x01\x3F")  # Column address: 0..319
            spidisplay.bus_write(SET_PAGE, b"\x00\x00\x00\xEF")  # Row address: 0..239        
