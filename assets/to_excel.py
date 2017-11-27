from xlwings import Workbook, Sheet, Range

class ToExcel():
    """
    Simplifica el uso de la libreria xlwings.
    Inicializa el
    """
    def __init__(self):
        self._wb = Workbook()
        self._i = 1

    def append(self, item, column='A', color=None):
        if type(item) == list:
            if type(item[0]) == list:
                index_increment = len(item)
            else:
                index_increment = 1
        else:
            index_increment = 1
        Range(column + str(self._i)).value = item
        if color is not None: 
            Range(column + str(self._i)).color = color
        self._i += index_increment

    def add_sheet(self, name):
        Sheet.add(name)
        self._i = 1

    def skip_line(self):
        self._i += 1

    def goto_line(self, line):
        self._i = line

    def goto_sheet(self, name):
        Sheet(name).activate()
        self._i = 1

    def rename_sheet(self):
        pass

    def index(self):
        return self._i

    def autofit(self):
        self._wb.active_sheet.autofit('c')

    def change_color(self, column, color):
        Range(column + str(self._i)).color = (255, 150, 150)

if __name__ == "__main__":
    x = ToExcel()
    x.append([[1,3,5,5], [1, 1, 2], [3, 4, 5]])