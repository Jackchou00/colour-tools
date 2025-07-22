import sys
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
)
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QTextCursor


# 全局异常捕获钩子
def log_exception_hook(exctype, value, tb):
    print("捕获到未处理的异常:")
    traceback.print_exception(exctype, value, tb)
    sys.__excepthook__(exctype, value, tb)


sys.excepthook = log_exception_hook

# 路径检查
CLI_EXE_PATH = os.path.join(os.path.dirname(__file__), "Debug", "RemoteCli.exe")
if not os.path.exists(CLI_EXE_PATH):
    print(f"严重错误: 无法找到相机控制程序: {CLI_EXE_PATH}")
    sys.exit(1)
else:
    print(f"成功找到相机控制程序: {CLI_EXE_PATH}")

from camera_controller import SonyCameraController


# --- 线程工作类 ---
class CameraWorker(QObject):
    connection_finished = pyqtSignal(bool)
    photo_finished = pyqtSignal(bool)
    disconnection_finished = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.camera = SonyCameraController(cli_path=CLI_EXE_PATH)

    @pyqtSlot()
    def run_connect_and_navigate(self):
        self.log_message.emit("开始连接相机...\n")
        try:
            is_connected = self.camera.connect_camera(1)
            if is_connected:
                self.log_message.emit("连接成功，正在导航到快门菜单...\n")
                navigated = self.camera.navigate_to_shutter()
                self.connection_finished.emit(navigated)
            else:
                self.log_message.emit("连接失败。\n")
                self.camera.disconnect()
                self.connection_finished.emit(False)
        except Exception as e:
            self.log_message.emit(f"连接时发生错误: {str(e)}\n")
            try:
                self.camera.disconnect()
            except:
                pass  # 忽略断开连接时的错误
            self.connection_finished.emit(False)

    @pyqtSlot()
    def run_take_photo(self):
        self.log_message.emit("正在拍照...\n")
        try:
            success = self.camera.take_photo()
            self.photo_finished.emit(success)
        except Exception as e:
            self.log_message.emit(f"拍照时发生错误: {str(e)}\n")
            self.photo_finished.emit(False)

    @pyqtSlot()
    def run_disconnect(self):
        self.log_message.emit("正在断开连接...\n")
        try:
            self.camera.disconnect()
            self.log_message.emit("连接已断开。\n")
        except Exception as e:
            self.log_message.emit(f"断开连接时发生错误: {str(e)}\n")
            self.log_message.emit("连接已强制断开。\n")
        finally:
            self.disconnection_finished.emit()


# --- 用于重定向 print 输出的类 ---
class EmittingStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

    def flush(self):
        pass


# --- 主窗口类 ---
class CameraUI(QMainWindow):
    start_connection = pyqtSignal()
    start_photo = pyqtSignal()
    start_disconnection = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sony 相机控制器 (PyQt5)")
        self.setGeometry(100, 100, 700, 500)

        self.connect_btn = QPushButton("连接相机")
        self.photo_btn = QPushButton("拍照")
        self.disconnect_btn = QPushButton("断开连接")
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(
            "QTextEdit { font-family: 'Courier New', monospace; }"
        )

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.photo_btn)
        button_layout.addWidget(self.disconnect_btn)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_output)
        self.setCentralWidget(central_widget)

        self.setup_thread()

        self.connect_btn.clicked.connect(self.on_connect_clicked)
        self.photo_btn.clicked.connect(self.on_photo_clicked)
        self.disconnect_btn.clicked.connect(self.on_disconnect_clicked)

        self.update_ui_state("disconnected")

        sys.stdout = EmittingStream(text_written=self.append_log)
        sys.stderr = EmittingStream(text_written=self.append_log)

        print("UI已启动。请点击 '连接相机'。\n")

    def setup_thread(self):
        self.thread = QThread()
        self.worker = CameraWorker()
        self.worker.moveToThread(self.thread)
        self.start_connection.connect(self.worker.run_connect_and_navigate)
        self.start_photo.connect(self.worker.run_take_photo)
        self.start_disconnection.connect(self.worker.run_disconnect)
        self.worker.connection_finished.connect(self.on_connection_finished)
        self.worker.photo_finished.connect(self.on_photo_finished)
        self.worker.disconnection_finished.connect(self.on_disconnection_finished)
        self.worker.log_message.connect(self.append_log)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @pyqtSlot(str)
    def append_log(self, text):
        """向日志窗口追加文本"""
        self.log_output.moveCursor(QTextCursor.MoveOperation.End)
        self.log_output.insertPlainText(text)

    def on_connect_clicked(self):
        self.log_output.clear()
        self.update_ui_state("connecting")
        self.start_connection.emit()

    def on_photo_clicked(self):
        self.update_ui_state("taking_photo")
        self.start_photo.emit()

    def on_disconnect_clicked(self):
        self.update_ui_state("disconnecting")
        self.start_disconnection.emit()

    @pyqtSlot(bool)
    def on_connection_finished(self, success):
        if success:
            self.append_log("\n--- 相机已就绪 ---\n")
            self.update_ui_state("connected")
        else:
            self.append_log("\n--- 连接失败，请检查相机或USB连接 ---\n")
            self.update_ui_state("disconnected")

    @pyqtSlot(bool)
    def on_photo_finished(self, success):
        if success:
            self.append_log(f"\n--- 拍照成功! ---\n")
        else:
            self.append_log("\n--- 拍照失败 ---\n")
        self.update_ui_state("connected")

    @pyqtSlot()
    def on_disconnection_finished(self):
        self.append_log("\n--- 已安全断开连接 ---\n")
        self.update_ui_state("disconnected")

    def update_ui_state(self, state: str):
        states = {
            "disconnected": (True, False, False, "连接相机", "拍照", "断开连接"),
            "connecting": (False, False, False, "连接中...", "拍照", "断开连接"),
            "connected": (False, True, True, "已连接", "拍照", "断开连接"),
            "taking_photo": (False, False, True, "已连接", "拍照中...", "断开连接"),
            "disconnecting": (False, False, False, "已连接", "拍照", "断开中..."),
        }
        enabled_conn, enabled_photo, enabled_disc, text_conn, text_photo, text_disc = (
            states[state]
        )
        self.connect_btn.setEnabled(enabled_conn)
        self.photo_btn.setEnabled(enabled_photo)
        self.disconnect_btn.setEnabled(enabled_disc)
        self.connect_btn.setText(text_conn)
        self.photo_btn.setText(text_photo)
        self.disconnect_btn.setText(text_disc)

    def closeEvent(self, event):
        print("正在关闭应用程序...")
        if self.disconnect_btn.isEnabled() or self.photo_btn.isEnabled():
            self.start_disconnection.emit()
            self.thread.quit()
            if not self.thread.wait(5000):
                print("警告: 等待工作线程退出超时。")
        else:
            self.thread.quit()
            self.thread.wait()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraUI()
    window.show()
    sys.exit(app.exec_())
