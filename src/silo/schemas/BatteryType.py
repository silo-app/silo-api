from enum import Enum


class BatteryType(Enum):
    AAA = "AAA"
    AA = "AA"
    C = "C"
    D = "D"
    BATTERY_18650 = "18650"
    BATTERY_18500 = "18500"
    BATTERY_17670 = "17670"
    BATTERY_16340_CR123A = "16340 (CR123A)"
    BATTERY_14500 = "14500"
    BATTERY_10440 = "10440"

    CR2032 = "CR2032"
    CR2025 = "CR2025"
    CR2016 = "CR2016"
    LR44_AG13 = "LR44 (AG13)"
    LR41_AG3 = "LR41 (AG3)"
    LR43_AG12 = "LR43 (AG12)"
    SR44_357_303 = "SR44 (357/303)"
    CR1632 = "CR1632"
    CR1220 = "CR1220"

    BLOCK_9V_6LR61 = "9V Block (6LR61)"
    LANTERN_6V = "6V Lantern Battery"
    AUTOMOTIVE_12V = "12V Automotive Battery"
    PRISMATIC_CELLS = "Prismatic Cells"
    CYLINDRICAL_CELLS = "Cylindrical Cells"
    BUTTON_CELLS = "Button Cells"

    @property
    def category(self) -> str:
        common_sizes = {
            self.AAA,
            self.AA,
            self.C,
            self.D,
            self.BATTERY_18650,
            self.BATTERY_18500,
            self.BATTERY_17670,
            self.BATTERY_16340_CR123A,
            self.BATTERY_14500,
            self.BATTERY_10440,
        }

        button_cells = {
            self.CR2032,
            self.CR2025,
            self.CR2016,
            self.LR44_AG13,
            self.LR41_AG3,
            self.LR43_AG12,
            self.SR44_357_303,
            self.CR1632,
            self.CR1220,
        }

        special_formats = {
            self.BLOCK_9V_6LR61,
            self.LANTERN_6V,
            self.AUTOMOTIVE_12V,
            self.PRISMATIC_CELLS,
            self.CYLINDRICAL_CELLS,
            self.BUTTON_CELLS,
        }

        if self in common_sizes:
            return "Common sizes"
        elif self in button_cells:
            return "Button cells"
        elif self in special_formats:
            return "Special formats"
        else:
            return "Unknown"
