import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTabWidget, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QHeaderView)
from PySide6.QtCore import Qt
import pandas as pd

class MainWindow(QMainWindow):
    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.setWindowTitle("Financial Management Dashboard")
        self.resize(1000, 700)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setup_overview_tab()
        self.setup_data_tab("Accounts Payable", self.data_model.ap_df)
        self.setup_data_tab("Accounts Receivable", self.data_model.ar_df)
        self.setup_data_tab("Expense Claims", self.data_model.expense_df)
        self.setup_data_tab("Budget Forecast", self.data_model.budget_df)
        self.setup_data_tab("General Ledger", self.data_model.gl_df)

    def setup_overview_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        lbl_title = QLabel("<h2>Executive Summary</h2>")
        layout.addWidget(lbl_title)

        kpi_layout = QHBoxLayout()
        
        # Calculate some KPIs
        ap_pending = self.data_model.ap_df[self.data_model.ap_df['Status'].isin(['Open', 'Partial'])]['Amount'].sum() if not self.data_model.ap_df.empty else 0
        ar_pending = self.data_model.ar_df[self.data_model.ar_df['Status'].isin(['Open', 'Partial'])]['Amount'].sum() if not self.data_model.ar_df.empty else 0
        exp_pending = self.data_model.expense_df[self.data_model.expense_df['Status'] == 'Submitted']['Amount'].sum() if not self.data_model.expense_df.empty else 0
        
        kpi_ap = self.create_kpi_card("Pending AP", f"${ap_pending:,.2f}")
        kpi_ar = self.create_kpi_card("Pending AR", f"${ar_pending:,.2f}")
        kpi_exp = self.create_kpi_card("Pending Expenses", f"${exp_pending:,.2f}")
        
        kpi_layout.addWidget(kpi_ap)
        kpi_layout.addWidget(kpi_ar)
        kpi_layout.addWidget(kpi_exp)
        
        layout.addLayout(kpi_layout)
        layout.addStretch()

        self.tabs.addTab(tab, "Overview")

    def create_kpi_card(self, title, value):
        card = QWidget()
        layout = QVBoxLayout(card)
        
        lbl_title = QLabel(f"<b>{title}</b>")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_value = QLabel(value)
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("font-size: 24px; color: #2C3E50;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        
        card.setStyleSheet("background-color: #ECF0F1; border-radius: 10px; padding: 20px;")
        return card

    def setup_data_tab(self, title, df):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Table
        table = QTableWidget()
        self.populate_table(table, df)
        layout.addWidget(table)

        # Export Button
        btn_layout = QHBoxLayout()
        btn_export = QPushButton(f"Export {title} to Excel")
        # Use a lambda to capture df
        btn_export.clicked.connect(lambda checked, d=df, t=title: self.export_data(d, t))
        btn_layout.addStretch()
        btn_layout.addWidget(btn_export)
        
        layout.addLayout(btn_layout)
        self.tabs.addTab(tab, title)

    def populate_table(self, table, df):
        if df.empty:
            return
            
        columns = list(df.columns)
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(df.shape[0])

        for row_idx, row in enumerate(df.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value) if not pd.isna(value) else "")
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable) # read-only for now
                table.setItem(row_idx, col_idx, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def export_data(self, df, title):
        if df.empty:
            QMessageBox.warning(self, "Export", "No data to export.")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, f"Export {title}", f"{title.replace(' ', '_')}_Export.xlsx", "Excel Files (*.xlsx)"
        )
        if filepath:
            success, msg = self.data_model.export_to_excel(df, filepath)
            if success:
                QMessageBox.information(self, "Export Successful", msg)
            else:
                QMessageBox.critical(self, "Export Failed", msg)
