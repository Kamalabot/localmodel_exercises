import sys
import json
import random
from datetime import datetime
from PySide6.QtCore import Qt, QSize, QRunnable, QThreadPool, Slot, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QListWidget, QStackedWidget, QLabel, QLineEdit, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)

# --- Threading Signals Bridge ---
class WorkerSignals(QObject):
    log = Signal(str)
    finished = Signal(str)

# --- Background Execution Ingestion Engine ---
class DatabaseIngestWorker(QRunnable):
    def __init__(self, db_type, config, mock_data):
        super().__init__()
        self.db_type = db_type
        self.config = config
        self.mock_data = mock_data
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.signals.log.emit(f"🚀 Initializing connection to {self.db_type}...")
            
            if self.db_type == "PostgreSQL":
                import psycopg2
                conn = psycopg2.connect(
                    host=self.config['host'], port=int(self.config['port']),
                    database=self.config['db'], user=self.config['user'], password=self.config['pass']
                )
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS system_logs (id TEXT, timestamp TEXT, event TEXT, payload TEXT);")
                cur.execute(
                    "INSERT INTO system_logs (id, timestamp, event, payload) VALUES (%s, %s, %s, %s);",
                    (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event'], json.dumps(self.mock_data))
                )
                conn.commit()
                cur.close()
                conn.close()

            elif self.db_type == "MySQL":
                import pymysql
                conn = pymysql.connect(
                    host=self.config['host'], port=int(self.config['port']),
                    database=self.config['db'], user=self.config['user'], password=self.config['pass']
                )
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS telemetry (id VARCHAR(50), ts VARCHAR(50), event VARCHAR(50));")
                cur.execute(
                    "INSERT INTO telemetry (id, ts, event) VALUES (%s, %s, %s);",
                    (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event'])
                )
                conn.commit()
                cur.close()
                conn.close()

            elif self.db_type == "MongoDB":
                from pymongo import MongoClient
                client = MongoClient(f"mongodb://{self.config['user']}:{self.config['pass']}@{self.config['host']}:{self.config['port']}/")
                db = client['lab_analytics']
                db['events'].insert_one(self.mock_data.copy())
                client.close()

            elif self.db_type == "Redis":
                import redis
                r = redis.Redis(host=self.config['host'], port=int(self.config['port']), password=self.config['pass'])
                r.set(f"log:{self.mock_data['id']}", json.dumps(self.mock_data))
                r.lpush("event_stream", self.mock_data['id'])

            elif self.db_type == "Meilisearch":
                import meilisearch
                client = meilisearch.Client(f"http://{self.config['host']}:{self.config['port']}", self.config['pass'])
                client.index('logs').add_documents([self.mock_data], primary_key='id')

            elif self.db_type == "Neo4j":
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(f"bolt://{self.config['host']}:{self.config['port']}", auth=(self.config['user'], self.config['pass']))
                with driver.session() as session:
                    session.run(
                        "MERGE (e:Event {id: $id}) SET e.timestamp = $ts, e.type = $event",
                        id=self.mock_data['id'], ts=self.mock_data['timestamp'], event=self.mock_data['event']
                    )
                driver.close()

            elif self.db_type == "Qdrant":
                from qdrant_client import QdrantClient
                from qdrant_client.models import PointStruct, VectorParams, Distance
                client = QdrantClient(host=self.config['host'], port=int(self.config['port']))
                vectors = [random.random(), random.random(), random.random()]
                client.recreate_collection(collection_name="events", vectors_config=VectorParams(size=3, distance=Distance.COSINE))
                client.upsert(
                    collection_name="events",
                    points=[PointStruct(id=random.randint(1, 100000), vector=vectors, payload=self.mock_data)]
                )

            elif self.db_type == "ClickHouse":
                from clickhouse_driver import Client
                client = Client(host=self.config['host'], port=int(self.config['port']))
                client.execute('CREATE TABLE IF NOT EXISTS events (id String, timestamp String, event String) ENGINE = Log')
                client.execute(
                    'INSERT INTO events (id, timestamp, event) VALUES',
                    [(self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event'])]
                )

            elif self.db_type == "DuckDB":
                import duckdb
                # Connect directly to the local persistent database file mapping
                conn = duckdb.connect(self.config['db_file'])
                conn.execute("CREATE TABLE IF NOT EXISTS memory_events (id VARCHAR, timestamp VARCHAR, event VARCHAR);")
                conn.execute(
                    "INSERT INTO memory_events VALUES (?, ?, ?);",
                    (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event'])
                )
                conn.close()

            elif self.db_type == "ObjectBox":
                # ObjectBox stores dynamic object properties based on custom bindings. 
                # Simulating structural persistence directly into the mount target path.
                with open(f"{self.config['data_dir']}/mock_objects.jsonl", "a") as f:
                    f.write(json.dumps(self.mock_data) + "\n")

            elif self.db_type == "SurrealDB":
                import requests
                # Connect via HTTP REST interface
                url = f"http://{self.config['host']}:{self.config['port']}/key/events/{self.mock_data['id']}"
                headers = {"Accept": "application/json", "NS": "test", "DB": "test"}
                auth = (self.config['user'], self.config['pass'])
                response = requests.put(url, json=self.mock_data, headers=headers, auth=auth)
                if response.status_code not in [200, 201]:
                    raise Exception(f"SurrealDB Error: {response.text}")

            self.signals.log.emit(f"✅ Data payload flushed successfully to {self.db_type}.")
            self.signals.finished.emit(self.db_type)
            
        except Exception as e:
            self.signals.log.emit(f"❌ Error feeding {self.db_type}: {str(e)}")

# --- Main Interface Framework ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified Multi-Paradigm Data Ingestion Node")
        self.setMinimumSize(QSize(1150, 700))
        self.thread_pool = QThreadPool()
        
        # Internal configuration storage lookup mappings
        self.db_meta = {
            "PostgreSQL": {"host": "localhost", "port": "5432", "db": "main_db", "user": "admin", "pass": "SecretPassword123"},
            "MySQL": {"host": "localhost", "port": "3306", "db": "main_db", "user": "admin", "pass": "SecretPassword123"},
            "MongoDB": {"host": "localhost", "port": "27017", "db": "admin", "user": "admin", "pass": "SecretPassword123"},
            "Redis": {"host": "localhost", "port": "6379", "db": "0", "user": "", "pass": "SecretPassword123"},
            "Meilisearch": {"host": "localhost", "port": "7700", "db": "", "user": "", "pass": "SecretMasterKey1234567890"},
            "Neo4j": {"host": "localhost", "port": "7687", "db": "", "user": "neo4j", "pass": "SecretPassword123"},
            "Qdrant": {"host": "localhost", "port": "6333", "db": "", "user": "", "pass": ""},
            "ClickHouse": {"host": "localhost", "port": "9000", "db": "default", "user": "default", "pass": ""},
            "DuckDB": {"db_file": "./duckdb_data/local_lab.db"},
            "ObjectBox": {"data_dir": "./objectbox_data"},
            "SurrealDB": {"host": "localhost", "port": "8000", "user": "root", "pass": "SecretPassword123"}
        }
        
        self.current_mock_data = {}
        self.input_fields_map = {}
        
        self.init_ui()
        self.generate_new_payload()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left Panel: Navigation lists
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Database Paradigm")
        title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #555;")
        self.db_list = QListWidget()
        self.db_list.addItems(list(self.db_meta.keys()))
        self.db_list.setCurrentRow(0)
        self.db_list.currentRowChanged.connect(self.switch_db_view)
        
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self.db_list)
        splitter.addWidget(sidebar_widget)
        
        # Right Panel: Configuration + Controls
        right_container = QSplitter(Qt.Vertical)
        top_workspace = QWidget()
        top_layout = QHBoxLayout(top_workspace)
        
        # Column 1: Configuration Form Forms
        self.config_stack = QStackedWidget()
        self.build_configuration_forms()
        
        config_box = QWidget()
        config_vbox = QVBoxLayout(config_box)
        config_vbox.addWidget(QLabel("<b>Network Connection Parameters</b>"))
        config_vbox.addWidget(self.config_stack)
        top_layout.addWidget(config_box, stretch=2)
        
        # Column 2: Data visibility Matrix
        preview_box = QWidget()
        preview_vbox = QVBoxLayout(preview_box)
        preview_vbox.addWidget(QLabel("<b>Outgoing Structured Document Payload</b>"))
        
        self.data_table = QTableWidget(3, 2)
        self.data_table.setHorizontalHeaderLabels(["Field Attribute", "Value Mapping"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        preview_vbox.addWidget(self.data_table)
        
        btn_layout = QHBoxLayout()
        gen_btn = QPushButton("Mutate Sample Payload")
        gen_btn.clicked.connect(self.generate_new_payload)
        send_btn = QPushButton("Commit to Stream")
        send_btn.setStyleSheet("background-color: #2b78e4; color: white; font-weight: bold;")
        send_btn.clicked.connect(self.fire_ingest_worker)
        btn_layout.addWidget(gen_btn)
        btn_layout.addWidget(send_btn)
        preview_vbox.addLayout(btn_layout)
        
        top_layout.addWidget(preview_box, stretch=3)
        right_container.addWidget(top_workspace)
        
        # Lower Workspace Segment: Log Terminal Console
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("<b>Standard Pipeline Execution Trace Log</b>"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("font-family: monospace; background-color: #1e1e1e; color: #d4d4d4;")
        log_layout.addWidget(self.console_output)
        
        log_widget.setFixedHeight(220)
        log_layout.addWidget(self.console_output)
        right_container.addWidget(log_widget)
        
        splitter.addWidget(right_container)
        splitter.setSizes([220, 930])

    def build_configuration_forms(self):
        for db_name, fields in self.db_meta.items():
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignTop)
            
            self.input_fields_map[db_name] = {}
            for field_key, default_val in fields.items():
                row = QHBoxLayout()
                lbl = QLabel(f"{field_key.replace('_', ' ').capitalize()}:")
                lbl.setMinimumWidth(80)
                line_edit = QLineEdit(default_val)
                row.addWidget(lbl)
                row.addWidget(line_edit)
                layout.addLayout(row)
                self.input_fields_map[db_name][field_key] = line_edit
                
            self.config_stack.addWidget(page)

    def switch_db_view(self, index):
        self.config_stack.setCurrentIndex(index)

    def generate_new_payload(self):
        events = ["USER_LOGIN", "PAYMENT_PROCESSED", "ORDER_CREATED", "CACHE_HIT", "SENSOR_ALERT", "NODE_DEPLOYED"]
        self.current_mock_data = {
            "id": f"tx-{random.randint(10000, 99999)}",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "event": random.choice(events)
        }
        
        for idx, (k, v) in enumerate(self.current_mock_data.items()):
            self.data_table.setItem(idx, 0, QTableWidgetItem(k))
            self.data_table.setItem(idx, 1, QTableWidgetItem(v))

    def append_log(self, message):
        self.console_output.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def fire_ingest_worker(self):
        selected_db = self.db_list.currentItem().text()
        
        runtime_config = {}
        for field_key, line_edit in self.input_fields_map[selected_db].items():
            runtime_config[field_key] = line_edit.text()
            
        worker = DatabaseIngestWorker(selected_db, runtime_config, self.current_mock_data)
        worker.signals.log.connect(self.append_log)
        worker.signals.finished.connect(lambda db: self.generate_new_payload())
        
        self.thread_pool.start(worker)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())