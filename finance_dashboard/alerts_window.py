from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from PySide6.QtCore import Qt

class AlertsWindow(QDialog):
    def __init__(self, data_model, parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.setWindowTitle("Past-Due Alerts Notification")
        self.resize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        lbl_info = QLabel("<b>Warning:</b> The following items are past their Due Date and remain unpaid/unreceived.")
        lbl_info.setStyleSheet("color: red; font-size: 14px;")
        layout.addWidget(lbl_info)

        # Get past due data
        past_due_ap = self.data_model.get_past_due_ap()
        past_due_ar = self.data_model.get_past_due_ar()

        if past_due_ap.empty and past_due_ar.empty:
            lbl_good = QLabel("No past-due items! Great job.")
            lbl_good.setStyleSheet("color: green; font-weight: bold;")
            layout.addWidget(lbl_good)
        else:
            if not past_due_ap.empty:
                layout.addWidget(QLabel("<b>Accounts Payable (Past Due):</b>"))
                self.table_ap = QTableWidget()
                self._populate_table(self.table_ap, past_due_ap, ['APID', 'Vendor', 'DueDate', 'Amount', 'Currency'])
                layout.addWidget(self.table_ap)

            if not past_due_ar.empty:
                layout.addWidget(QLabel("<b>Accounts Receivable (Past Due):</b>"))
                self.table_ar = QTableWidget()
                self._populate_table(self.table_ar, past_due_ar, ['ARID', 'Customer', 'DueDate', 'Amount', 'Currency'])
                layout.addWidget(self.table_ar)

        btn_box = QHBoxLayout()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(btn_close)
        layout.addLayout(btn_box)

    def _populate_table(self, table, df, columns):
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(df.shape[0])

        for row_idx, row in enumerate(df[columns].itertuples(index=False)):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) # read-only
                table.setItem(row_idx, col_idx, item)
        
        table.resizeColumnsToContents()
