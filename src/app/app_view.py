import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QLabel,
    QAbstractItemView,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QThread, Signal, QSettings
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont

# 🔥 关键修复：从core导入处理函数，不再导入main，无循环！
from .app_viewmodel import process_excel_to_files


# -------------------------- 工作线程 --------------------------
class ProcessWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int)
    finished_signal = Signal(bool, str)

    def __init__(self, excel_files, output_base_dir):
        super().__init__()
        self.excel_files = excel_files
        self.output_base_dir = output_base_dir

    def run(self):
        total = len(self.excel_files)
        if total == 0:
            self.finished_signal.emit(False, "没有待处理的Excel文件")
            return

        success_count = 0
        for idx, excel_path in enumerate(self.excel_files, 1):
            file_name = os.path.basename(excel_path)
            self.log_signal.emit(f"\n>>> 开始处理 [{idx}/{total}]: {file_name}")
            base_name = os.path.splitext(file_name)[0]
            output_dir = os.path.join(self.output_base_dir, base_name)
            self.log_signal.emit(f"    输出目录: {output_dir}")

            success = process_excel_to_files(excel_path, output_dir, log_callback=self.log_signal.emit)
            if success:
                success_count += 1
                self.log_signal.emit(f"<<< 完成处理: {file_name}\n")
            else:
                self.log_signal.emit(f"<<< 处理失败: {file_name}\n")
            self.progress_signal.emit(idx, total)

        final_msg = f"处理完成！成功 {success_count}/{total} 个文件。"
        self.finished_signal.emit(success_count == total, final_msg)


# -------------------------- 主窗口UI --------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel数据导出工具")
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)

        self.settings = QSettings("MyCompany", "ExcelExportTool")
        self.last_output_dir = self.settings.value("last_output_dir", "")
        if not self.last_output_dir or not os.path.exists(self.last_output_dir):
            self.last_output_dir = "C:/"

        self.setup_ui()
        self.worker = None

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        output_layout = QHBoxLayout()
        output_label = QLabel("输出根目录:")
        self.output_line_edit = QLineEdit()
        self.output_line_edit.setText(self.last_output_dir)
        self.output_line_edit.textChanged.connect(self.save_output_dir)
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_line_edit, 1)
        output_layout.addWidget(browse_btn)
        main_layout.addLayout(output_layout)

        list_label = QLabel("Excel文件列表（支持拖拽添加，选中后按Delete删除）:")
        main_layout.addWidget(list_label)
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.file_list_widget.setAcceptDrops(True)
        self.file_list_widget.installEventFilter(self)
        main_layout.addWidget(self.file_list_widget)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始运行")
        self.start_btn.clicked.connect(self.start_processing)
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.clear_file_list)
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        log_label = QLabel("处理日志:")
        main_layout.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        main_layout.addWidget(self.log_text)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出根目录", self.output_line_edit.text())
        if dir_path:
            self.output_line_edit.setText(dir_path)

    def save_output_dir(self):
        current_dir = self.output_line_edit.text()
        if current_dir:
            self.settings.setValue("last_output_dir", current_dir)

    def clear_file_list(self):
        self.file_list_widget.clear()

    def remove_selected(self):
        for item in self.file_list_widget.selectedItems():
            self.file_list_widget.takeItem(self.file_list_widget.row(item))

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 记录到临时文件，便于打包后排查
        with open("E:/temp/drag_log.txt", "a") as f:
            f.write(f"dragEnterEvent: formats={event.mimeData().formats()}, hasUrls={event.mimeData().hasUrls()}\n")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path and self.is_excel_file(file_path):
                if not self.is_file_in_list(file_path):
                    self.file_list_widget.addItem(file_path)
        event.acceptProposedAction()

    def is_excel_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in [".xlsx", ".xls"]

    def is_file_in_list(self, path):
        for i in range(self.file_list_widget.count()):
            if self.file_list_widget.item(i).text() == path:
                return True
        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.remove_selected()
        else:
            super().keyPressEvent(event)

    def start_processing(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "提示", "已有处理任务正在运行，请等待完成")
            return

        output_base = self.output_line_edit.text().strip()
        if not output_base:
            QMessageBox.warning(self, "提示", "请设置输出根目录")
            return
        try:
            os.makedirs(output_base, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建输出目录: {e}")
            return

        excel_files = []
        for i in range(self.file_list_widget.count()):
            file_path = self.file_list_widget.item(i).text()
            if os.path.exists(file_path):
                excel_files.append(file_path)
            else:
                QMessageBox.warning(self, "文件不存在", f"文件不存在，已忽略: {file_path}")

        if not excel_files:
            QMessageBox.warning(self, "提示", "请先添加有效的Excel文件")
            return

        self.log_text.clear()
        self.log_text.append("开始批量处理...\n")
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(excel_files))
        self.progress_bar.setValue(0)

        self.worker = ProcessWorker(excel_files, output_base)
        self.worker.log_signal.connect(self.append_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.on_processing_finished)
        self.worker.start()

    def append_log(self, text):
        self.log_text.append(text)
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        QApplication.processEvents()

    def update_progress(self, current, total):
        self.progress_bar.setValue(current)

    def on_processing_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(True)
        self.append_log(f"\n{message}")
        if success:
            QMessageBox.information(self, "完成", message)
        else:
            QMessageBox.warning(self, "处理完成但有错误", message)
