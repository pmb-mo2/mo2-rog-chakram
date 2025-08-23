import sys
if sys.platform == "win32":
    import ctypes
    SPI_GETMOUSESPEED = 0x0070
    SPI_SETMOUSESPEED = 0x0071
    SPIF_SENDCHANGE = 0x02

    def get_mouse_speed() -> int:
        speed = ctypes.c_int()
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0
        )
        return speed.value

    def set_mouse_speed(speed: int) -> None:
        ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETMOUSESPEED, 0, speed, SPIF_SENDCHANGE
        )
else:
    def get_mouse_speed() -> int:
        return 10

    def set_mouse_speed(speed: int) -> None:
        pass
