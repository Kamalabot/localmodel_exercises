import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from data_model import DataModel
from main_window import MainWindow
from alerts_window import AlertsWindow

def main():
    app = QApplication(sys.argv)
    
    # Load Data
    data_model = DataModel()
    
    # Initialize Main Window
    main_win = MainWindow(data_model)
    main_win.show()
    
    # Check for past-due items and show alert window if any exist
    past_due_ap = data_model.get_past_due_ap()
    past_due_ar = data_model.get_past_due_ar()
    
    if not past_due_ap.empty or not past_due_ar.empty:
        alerts_win = AlertsWindow(data_model, parent=main_win)
        alerts_win.exec() # Modal dialog

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
