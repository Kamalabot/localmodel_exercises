import sys
import json
import random
import socket
from datetime import datetime

from PySide6.QtCore import Qt, QSize, QRunnable, QThreadPool, Signal, QObject, QThread, Slot
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QListWidget, QStackedWidget, QLabel, QLineEdit, QPushButton, 
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter
)
import paramiko

VM_IP = "192.168.31.180"
COMPOSE_FILE = "custom-compose.yml"
SSH_USER = "vboxuser"
SSH_PASS = "1234"

SERVICE_MAPPING = {
    "PostgreSQL": "postgres",
    "MySQL": "mysql",
    "MongoDB": "mongodb",
    "Redis": "redis-memory",
    "Meilisearch": "meilisearch",
    "ClickHouse": "clickhouse",
    "SurrealDB": "surrealdb",
    "Neo4j": "neo4j",
    "Qdrant": "qdrant"
}

# --- Asynchronous SSH Framework Container ---
class SSHWorkerSignals(QObject):
    log = Signal(str)
    finished = Signal()


class SSHDockerWorker(QThread):
    """Background worker to isolate blocking Paramiko SSH socket connections."""
    def __init__(self, host, username, password, command, service):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password
        self.command = command
        self.service = service
        self.signals = SSHWorkerSignals()

    def run(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.signals.log.emit(f"🐳 Connecting to Remote Host Engine via SSH at {self.host}...")
            ssh.connect(self.host, username=self.username, password=self.password, timeout=10)
            
            self.signals.log.emit(f"🚀 Dispatching remote container optimization layers...")
            stdin, stdout, stderr = ssh.exec_command(self.command)
            
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            
            if exit_status == 0:
                self.signals.log.emit(f"✅ Docker remote start signal accepted for {self.service}.")
                self.signals.finished.emit()
            else:
                combined_err = error if error else output
                self.signals.log.emit(f"⚠️ Remote SSH/Docker Error (Code {exit_status}): {combined_err}")
                
        except Exception as e:
            self.signals.log.emit(f"❌ SSH Connection Refused: {str(e)}")
        finally:
            ssh.close()


# --- Exception-Safe ThreadPool Core Worker ---
class TaskSignals(QObject):
    log = Signal(str)
    data_fetched = Signal(list, list)
    finished = Signal()


class DatabaseTaskWorker(QRunnable):
    def __init__(self, action_type, db_name, config, mock_data=None):
        super().__init__()
        self.action_type = action_type # "stream_payload" or "fetch_view"
        self.db_name = db_name
        self.config = config
        self.mock_data = mock_data
        self.signals = TaskSignals()

    def run(self):
        try:
            if self.action_type == "stream_payload":
                self.commit_payload_direct()
            elif self.action_type == "fetch_view":
                self.execute_data_fetch()
        except Exception as general_fault:
            self.signals.log.emit(f"💥 Thread Pool Runtime Fault: {str(general_fault)}")
        finally:
            self.signals.finished.emit()

    def commit_payload_direct(self):
        self.signals.log.emit(f"🚀 Initializing payload transmission block for {self.db_name}...")
        try:
            if self.db_name == "PostgreSQL":
                import psycopg2
                conn = psycopg2.connect(host=VM_IP, port=int(self.config['port']), database=self.config['db'], user=self.config['user'], password=self.config['pass'], connect_timeout=3)
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS system_logs (id TEXT PRIMARY KEY, timestamp TEXT, event TEXT);")
                cur.execute("INSERT INTO system_logs VALUES (%s, %s, %s);", (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event']))
                conn.commit(); cur.close(); conn.close()

            elif self.db_name == "MySQL":
                import pymysql
                conn = pymysql.connect(host=VM_IP, port=int(self.config['port']), database=self.config['db'], user=self.config['user'], password=self.config['pass'], connect_timeout=3)
                cur = conn.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS telemetry (id VARCHAR(50) PRIMARY KEY, ts VARCHAR(50), event VARCHAR(50));")
                cur.execute("INSERT INTO telemetry VALUES (%s, %s, %s);", (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event']))
                conn.commit(); cur.close(); conn.close()

            elif self.db_name == "MongoDB":
                from pymongo import MongoClient
                client = MongoClient(f"mongodb://{self.config['user']}:{self.config['pass']}@{VM_IP}:{self.config['port']}/", serverSelectionTimeoutMS=3000)
                client['lab_analytics']['events'].insert_one(self.mock_data.copy())
                client.close()

            elif self.db_name == "Redis":
                import redis
                r = redis.Redis(host=VM_IP, port=int(self.config['port']), password=self.config['pass'], socket_timeout=3)
                r.set(f"log:{self.mock_data['id']}", json.dumps(self.mock_data))

            elif self.db_name == "Meilisearch":
                import meilisearch
                client = meilisearch.Client(f"http://{VM_IP}:{self.config['port']}", self.config['pass'], timeout=3)
                client.index('logs').add_documents([self.mock_data], primary_key='id')

            elif self.db_name == "ClickHouse":
                from clickhouse_driver import Client
                client = Client(host=VM_IP, port=int(self.config['port']), connect_timeout=3)
                client.execute('CREATE TABLE IF NOT EXISTS events (id String, timestamp String, event String) ENGINE = Log')
                client.execute('INSERT INTO events (id, timestamp, event) VALUES', [(self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event'])])

            elif self.db_name == "DuckDB":
                import duckdb
                conn = duckdb.connect(self.config['db_file'])
                conn.execute("CREATE TABLE IF NOT EXISTS memory_events (id VARCHAR PRIMARY KEY, timestamp VARCHAR, event VARCHAR);")
                conn.execute("INSERT INTO memory_events VALUES (?, ?, ?);", (self.mock_data['id'], self.mock_data['timestamp'], self.mock_data['event']))
                conn.close()

            elif self.db_name == "SurrealDB":
                import requests
                url = f"http://{VM_IP}:{self.config['port']}/key/events/{self.mock_data['id']}"
                requests.put(url, json=self.mock_data, headers={"NS": "test", "DB": "test"}, auth=(self.config['user'], self.config['pass']), timeout=3)

            elif self.db_name == "Neo4j":
                from neo4j import GraphDatabase
                with GraphDatabase.driver(f"bolt://{VM_IP}:{self.config['port']}", auth=(self.config['user'], self.config['pass']), connection_timeout=3) as driver:
                    with driver.session() as session:
                        session.run("MERGE (e:Event {id: $id}) SET e.timestamp = $ts, e.type = $event", id=self.mock_data['id'], ts=self.mock_data['timestamp'], event=self.mock_data['event'])

            elif self.db_name == "Qdrant":
                from qdrant_client import QdrantClient
                from qdrant_client.models import PointStruct, VectorParams, Distance
                client = QdrantClient(host=VM_IP, port=int(self.config['port']), timeout=3)
                client.recreate_collection(collection_name="events", vectors_config=VectorParams(size=3, distance=Distance.COSINE))
                client.upsert(collection_name="events", points=[PointStruct(id=random.randint(1, 100000), vector=[0.1, 0.5, 0.9], payload=self.mock_data)])

            self.signals.log.emit(f"✅ Ingestion successful for target database: {self.db_name}")
        except Exception as error_context:
            self.signals.log.emit(f"❌ Connection/Ingest Refused on {self.db_name}: {str(error_context)}")
    
    def execute_data_fetch(self):
        try:
            headers, rows = ["Attributes"], [["No active data structure layout initialized"]]
            
            if self.db_name == "PostgreSQL":
                import psycopg2
                conn = psycopg2.connect(host=VM_IP, port=int(self.config['port']), database=self.config['db'], user=self.config['user'], password=self.config['pass'], connect_timeout=2)
                cur = conn.cursor()
                cur.execute("SELECT id, timestamp, event FROM system_logs ORDER BY timestamp DESC LIMIT 10;")
                rows, headers = [list(r) for r in cur.fetchall()], ["ID", "Timestamp", "Event"]
                cur.close(); conn.close()

            elif self.db_name == "MySQL":
                import pymysql
                conn = pymysql.connect(host=VM_IP, port=int(self.config['port']), database=self.config['db'], user=self.config['user'], password=self.config['pass'], connect_timeout=2)
                cur = conn.cursor()
                cur.execute("SELECT id, ts, event FROM telemetry ORDER BY ts DESC LIMIT 10;")
                rows, headers = [list(r) for r in cur.fetchall()], ["ID", "Timestamp", "Event"]
                cur.close(); conn.close()

            elif self.db_name == "MongoDB":
                from pymongo import MongoClient
                client = MongoClient(f"mongodb://{self.config['user']}:{self.config['pass']}@{VM_IP}:{self.config['port']}/", serverSelectionTimeoutMS=2000)
                cursor = client['lab_analytics']['events'].find().sort("timestamp", -1).limit(10)
                rows, headers = [[str(d.get('_id')), d.get('id', ''), d.get('event', '')] for d in cursor], ["BSON ID", "Business ID", "Event"]
                client.close()

            elif self.db_name == "Redis":
                import redis
                r = redis.Redis(host=VM_IP, port=int(self.config['port']), password=self.config['pass'], socket_timeout=2)
                keys = r.keys("log:*")[:10]
                rows, headers = [[k.decode('utf-8'), r.get(k).decode('utf-8')[:60]] for k in keys], ["Key Name", "Value Mapping Data"]

            elif self.db_name == "ClickHouse":
                from clickhouse_driver import Client
                client = Client(host=VM_IP, port=int(self.config['port']), connect_timeout=2)
                rows, headers = client.execute('SELECT id, timestamp, event FROM events ORDER BY timestamp DESC LIMIT 10'), ["ID", "Timestamp", "Event"]

            elif self.db_name == "DuckDB":
                import duckdb
                conn = duckdb.connect(self.config['db_file'])
                rows, headers = conn.execute("SELECT id, timestamp, event FROM memory_events LIMIT 10;").fetchall(), ["ID", "Timestamp", "Event"]
                conn.close()

            elif self.db_name == "SurrealDB":
                import requests
                url = f"http://{VM_IP}:{self.config['port']}/sql"
                headers_auth = {"NS": "test", "DB": "test", "Accept": "application/json"}
                q_payload = "SELECT id, timestamp, event FROM events ORDER BY timestamp DESC LIMIT 10;"
                response = requests.post(url, data=q_payload, headers=headers_auth, auth=(self.config['user'], self.config['pass']), timeout=2)
                if response.status_code == 200:
                    json_res = response.json()
                    if json_res and isinstance(json_res, list) and 'result' in json_res[0]:
                        records = json_res[0]['result']
                        rows = [[r.get('id', ''), r.get('timestamp', ''), r.get('event', '')] for r in records]
                        headers = ["Surreal ID", "Timestamp", "Event Type"]

            elif self.db_name == "Meilisearch":
                import meilisearch
                client = meilisearch.Client(f"http://{VM_IP}:{self.config['port']}", self.config['pass'], timeout=2)
                result = client.index('logs').search('', {'limit': 10})
                hits = result.get('hits', [])
                rows = [[h.get('id', ''), h.get('timestamp', ''), h.get('event', '')] for h in hits]
                headers = ["Meili Document ID", "Timestamp", "Indexed Event"]

            elif self.db_name == "Neo4j":
                from neo4j import GraphDatabase
                with GraphDatabase.driver(f"bolt://{VM_IP}:{self.config['port']}", auth=(self.config['user'], self.config['pass']), connection_timeout=2) as driver:
                    with driver.session() as session:
                        result = session.run("MATCH (e:Event) RETURN e.id AS id, e.timestamp AS ts, e.type AS type ORDER BY ts DESC LIMIT 10;")
                        rows = [[record["id"], record["ts"], record["type"]] for record in result]
                        headers = ["Graph Node ID", "Property: Timestamp", "Property: Type"]

            elif self.db_name == "Qdrant":
                from qdrant_client import QdrantClient
                client = QdrantClient(host=VM_IP, port=int(self.config['port']), timeout=2)
                points, _ = client.scroll(collection_name="events", limit=10, with_payload=True, with_vectors=False)
                rows = []
                for pt in points:
                    payload = pt.payload or {}
                    rows.append([str(pt.id), payload.get('id', ''), payload.get('event', '')])
                headers = ["Vector Point ID", "Payload Business ID", "Payload Event"]

            self.signals.data_fetched.emit(headers, rows)
        except Exception as fetch_fault:
            self.signals.data_fetched.emit(["Storage Status"], [[f"Connection failed or schema uninitialized: {str(fetch_fault)}"]])


# --- Primary Display Component Frame ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data-Oriented Safe Engine Orchestrator")
        self.setMinimumSize(QSize(1250, 750))
        self.thread_pool = QThreadPool()
        
        self.db_meta = {
            "PostgreSQL": {"port": "5432", "db": "main_db", "user": "admin", "pass": "SecretPassword123"},
            "MySQL": {"port": "3306", "db": "main_db", "user": "admin", "pass": "SecretPassword123"},
            "MongoDB": {"port": "27017", "db": "admin", "user": "admin", "pass": "SecretPassword123"},
            "Redis": {"port": "6379", "pass": "SecretPassword123"},
            "Meilisearch": {"port": "7700", "pass": "SecretMasterKey1234567890"},
            "ClickHouse": {"port": "9000", "db": "default", "user": "default", "pass": ""},
            "SurrealDB": {"port": "8000", "user": "root", "pass": "SecretPassword123"},
            "Neo4j": {"port": "7687", "user": "neo4j", "pass": "SecretPassword123"},
            "Qdrant": {"port": "6333"},
            "DuckDB": {"db_file": "./duckdb_data/local_lab.db"},
            "ObjectBox": {"data_dir": "./objectbox_data"}
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
        
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.addWidget(QLabel("<b>Database Stack Targets</b>"))
        self.db_list = QListWidget()
        self.db_list.addItems(list(self.db_meta.keys()))
        self.db_list.setCurrentRow(0)
        self.db_list.currentRowChanged.connect(self.switch_db_view)
        sidebar_layout.addWidget(self.db_list)
        splitter.addWidget(sidebar_widget)
        
        right_container = QSplitter(Qt.Vertical)
        top_workspace = QWidget()
        top_layout = QHBoxLayout(top_workspace)
        
        self.config_stack = QStackedWidget()
        self.build_configuration_forms()
        config_box = QWidget()
        config_vbox = QVBoxLayout(config_box)
        config_vbox.addWidget(QLabel(f"<b>Connection Properties: {VM_IP}</b>"))
        config_vbox.addWidget(self.config_stack)
        top_layout.addWidget(config_box, stretch=2)
        
        preview_box = QWidget()
        preview_vbox = QVBoxLayout(preview_box)
        preview_vbox.addWidget(QLabel("<b>Active Document Payload Model</b>"))
        self.payload_table = QTableWidget(3, 2)
        self.payload_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        preview_vbox.addWidget(self.payload_table)
        
        btn_layout = QVBoxLayout()
        boot_btn = QPushButton("⚙️ Boot Service Container")
        boot_btn.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        boot_btn.clicked.connect(lambda: self.run_task("start_service"))
        
        send_btn = QPushButton("🚀 Commit Payload Ingestion")
        send_btn.setStyleSheet("background-color: #2b78e4; color: white; font-weight: bold;")
        send_btn.clicked.connect(lambda: self.run_task("stream_payload"))
        
        mutate_btn = QPushButton("Mutate Local Structural Values")
        mutate_btn.clicked.connect(self.generate_new_payload)
        
        btn_layout.addWidget(boot_btn)
        btn_layout.addWidget(send_btn)
        btn_layout.addWidget(mutate_btn)
        preview_vbox.addLayout(btn_layout)
        top_layout.addWidget(preview_box, stretch=3)
        right_container.addWidget(top_workspace)
        
        data_inspect_box = QWidget()
        inspect_vbox = QVBoxLayout(data_inspect_box)
        inspect_vbox.addWidget(QLabel("<b>Live Server Storage State Table Viewer</b>"))
        self.viewer_table = QTableWidget(0, 0)
        inspect_vbox.addWidget(self.viewer_table)
        right_container.addWidget(data_inspect_box)
        
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.addWidget(QLabel("<b>Pipeline Orchestration Trace Terminal Logs</b>"))
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("font-family: monospace; background-color: #121212; color: #a4a4a4;")
        log_layout.addWidget(self.console_output)
        right_container.addWidget(log_widget)
        
        splitter.addWidget(right_container)
        splitter.setSizes([200, 1050])
        right_container.setSizes([280, 260, 180])

    def build_configuration_forms(self):
        for db_name, fields in self.db_meta.items():
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setAlignment(Qt.AlignTop)
            self.input_fields_map[db_name] = {}
            for k, default in fields.items():
                row = QHBoxLayout()
                row.addWidget(QLabel(f"{k.capitalize()}:"))
                line_edit = QLineEdit(default)
                row.addWidget(line_edit)
                layout.addLayout(row)
                self.input_fields_map[db_name][k] = line_edit
            self.config_stack.addWidget(page)

    def switch_db_view(self, index):
        self.config_stack.setCurrentIndex(index)
        self.run_task("fetch_view")

    def generate_new_payload(self):
        events = ["USER_LOGIN", "PAYMENT_PROCESSED", "ORDER_CREATED", "CACHE_HIT", "SENSOR_ALERT"]
        self.current_mock_data = {
            "id": f"tx-{random.randint(10000, 99999)}",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "event": random.choice(events)
        }
        self.payload_table.setRowCount(len(self.current_mock_data))
        self.payload_table.setColumnCount(2)
        for idx, (k, v) in enumerate(self.current_mock_data.items()):
            self.payload_table.setItem(idx, 0, QTableWidgetItem(k))
            self.payload_table.setItem(idx, 1, QTableWidgetItem(v))

    def append_log(self, msg):
        self.console_output.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def boot_docker_node_ssh(self, selected_db, current_config):
        """Asynchronously dispatches the Remote Paramiko Core Infrastructure orchestration."""
        service = SERVICE_MAPPING.get(selected_db)
        if not service:
            self.append_log(f"ℹ️ {selected_db} operates as an in-process local framework. No Docker profile target required.")
            return

        self.append_log(f"🐳 Dispatching remote Paramiko SSH command for: [{service}]...")
        
        # Inject standard multi-profile targeting criteria safely
        remote_cmd = f"docker compose -f {COMPOSE_FILE} --profile manual up -d {service}"

        # Initialize the background thread worker to decouple completely from GUI loops
        self.ssh_worker = SSHDockerWorker(
            host=VM_IP, 
            username=SSH_USER, 
            password=SSH_PASS, 
            command=remote_cmd,
            service=service
        )

        # Connect internal telemetry streams safely back into the runtime console layout
        self.ssh_worker.signals.log.connect(self.append_log)
        
        # Trigger validation handshake when execution succeeds
        def on_successful_boot():
            self.verify_socket_handshake_local(current_config)
            self.run_task("fetch_view")

        self.ssh_worker.signals.finished.connect(on_successful_boot)
        self.ssh_worker.finished.connect(self.ssh_worker.deleteLater)
        
        # Fire background execution
        self.ssh_worker.start()

    def verify_socket_handshake_local(self, config):
        port = int(config.get('port', 0))
        if not port:
            return
        
        self.append_log(f"🔍 Monitoring socket path availability at {VM_IP}:{port}...")
        for attempt in range(1, 7):
            QThread.msleep(5000) # Non-blocking safe thread sleep substitution pattern
            try:
                with socket.create_connection((VM_IP, port), timeout=2):
                    self.append_log(f"✨ Port {port} responded successfully. Database listener is alive.")
                    return
            except (socket.timeout, ConnectionRefusedError):
                self.append_log(f"⏳ Port {port} refused connection. Engine is booting ({attempt}/6)...")
        self.append_log(f"⚠️ Port {port} did not answer within the grace window. Operations might fail.")

    def run_task(self, action_type):
        selected_db = self.db_list.currentItem().text()
        config = {}
        for k, line_edit in self.input_fields_map[selected_db].items():
            config[k] = line_edit.text()
            
        # Route 'start_service' exclusively through the QThread SSH orchestration pipeline
        if action_type == "start_service":
            self.boot_docker_node_ssh(selected_db, config)
            return

        # Fallback handling for data tasks inside standard threadpools
        worker = DatabaseTaskWorker(action_type, selected_db, config, self.current_mock_data)
        worker.signals.log.connect(self.append_log)
        worker.signals.data_fetched.connect(self.populate_viewer_grid)
        if action_type == "stream_payload":
            worker.signals.finished.connect(lambda: self.run_task("fetch_view"))
            
        self.thread_pool.start(worker)

    def populate_viewer_grid(self, headers, rows):
        self.viewer_table.setRowCount(len(rows))
        self.viewer_table.setColumnCount(len(headers))
        self.viewer_table.setHorizontalHeaderLabels(headers)
        self.viewer_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for r_idx, row in enumerate(rows):
            for c_idx, val in enumerate(row):
                self.viewer_table.setItem(r_idx, c_idx, QTableWidgetItem(str(val)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())