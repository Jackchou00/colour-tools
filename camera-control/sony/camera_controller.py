import subprocess
import os
import time
import threading
from pathlib import Path
from typing import Optional, List, Tuple


class SonyCameraController:
    def __init__(self, cli_path: str = None):
        if cli_path is None:
            cli_path = os.path.join(os.path.dirname(__file__), "Debug", "RemoteCli.exe")

        self.cli_path = cli_path
        self.process: Optional[subprocess.Popen] = None
        self.connected = False
        self.camera_info = None

    def start_cli(self) -> bool:
        try:
            self.process = subprocess.Popen(
                [self.cli_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.path.dirname(self.cli_path),
            )
            return True
        except Exception as e:
            print(f"Failed to start CLI: {e}")
            return False

    def read_output_until(self, expected_text: str, timeout: int = 10) -> str:
        output = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                break

            try:
                char = self.process.stdout.read(1)
                if char:
                    output += char
                    print(char, end="", flush=True)
                    if expected_text in output:
                        break
            except Exception:
                break

        return output

    def read_output_until_multiple(
        self, expected_texts: List[str], timeout: int = 10
    ) -> str:
        """等待直到出现任意一个预期文本"""
        output = ""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.process.poll() is not None:
                break

            try:
                char = self.process.stdout.read(1)
                if char:
                    output += char
                    print(char, end="", flush=True)
                    # 检查是否匹配任意预期文本
                    for expected_text in expected_texts:
                        if expected_text in output:
                            return output
            except Exception:
                break

        return output

    def send_input(self, command: str) -> bool:
        """发送输入到CLI进程，返回是否成功"""
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
                return True
            except (OSError, BrokenPipeError) as e:
                print(f"发送输入失败: {e}")
                return False
        else:
            print("进程已结束，无法发送输入")
            return False

    def connect_camera(self, camera_index: int = 1) -> bool:
        if not self.start_cli():
            return False

        print("等待相机枚举...")
        output = self.read_output_until_multiple(
            ["Connect to camera with input number...", "No cameras detected"],
            timeout=15,
        )
        # time.sleep(1)  # 增加延时

        # 检查是否没有检测到相机
        if "No cameras detected" in output:
            print("未检测到相机，请检查:")
            print("1. 相机是否已连接USB线")
            print("2. 相机是否已开机")
            print("3. 相机是否设置为正确的USB模式")
            print("4. USB线是否正常工作")
            self.cleanup()
            return False

        # 检查进程是否仍在运行
        if self.process.poll() is not None:
            print("CLI程序已退出")
            return False

        if "detected" not in output:
            print("未检测到相机")
            self.cleanup()
            return False

        print(f"\n发送相机连接命令: {camera_index}")
        if not self.send_input(str(camera_index)):
            print("发送连接命令失败")
            self.cleanup()
            return False

        # time.sleep(1)  # 增加延时

        # 等待TOP-MENU出现
        output = self.read_output_until("TOP-MENU", timeout=15)

        if "TOP-MENU" in output:
            print(f"\n相机连接成功，进入TOP-MENU!")

            # 输入1进入Remote Control Mode
            print("选择Remote Control Mode...")
            self.send_input("1")
            # time.sleep(1)  # 增加延时

            # 等待REMOTE-MENU出现或连接失败消息
            output = self.read_output_until_multiple(
                ["REMOTE-MENU", "connection failed", "Please input '0'"], timeout=15
            )

            # 处理连接失败的情况
            if "connection failed" in output or "Please input '0'" in output:
                print("相机连接失败，尝试重试...")
                print("返回TOP-MENU...")
                self.send_input("0")  # 返回TOP-MENU
                time.sleep(2)  # 等待返回

                # 重新尝试进入Remote Control Mode
                print("重新选择Remote Control Mode...")
                self.send_input("1")
                # time.sleep(1)

                # 再次等待REMOTE-MENU
                output = self.read_output_until("REMOTE-MENU", timeout=15)

            if "REMOTE-MENU" in output:
                self.connected = True
                print("成功进入Remote Control Mode!")
                return True

        print("相机连接失败")
        self.cleanup()
        return False

    def cleanup(self):
        """清理资源，关闭进程"""
        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                print(f"清理进程时出错: {e}")
            finally:
                self.process = None
                self.connected = False

    def navigate_to_shutter(self) -> bool:
        if not self.connected:
            print("相机未连接")
            return False

        print("\n进入快门操作菜单...")
        # 输入1进入Shutter/Rec Operation Menu
        if not self.send_input("1"):
            print("发送菜单选择命令失败")
            return False
        # time.sleep(1)  # 增加延时

        # 等待Shutter/Rec Operation Menu出现
        output = self.read_output_until("Shutter/Rec Operation Menu", timeout=10)

        if "Shutter/Rec Operation Menu" in output:
            print("成功进入Shutter/Rec Operation Menu!")
            return True
        else:
            print("无法进入快门操作菜单")
            return False

    def take_photo(self) -> bool:
        if not self.connected:
            print("相机未连接")
            return False

        print("\n触发快门释放...")
        if not self.send_input("1"):  # 在Shutter/Rec Operation Menu中输入1进行快门释放
            print("发送快门命令失败")
            return False
        # time.sleep(1)  # 增加延时

        # 等待拍照过程完成，寻找"Shutter down"和"Shutter up"
        output = self.read_output_until("Shutter up", timeout=15)

        if "Shutter down" in output and "Shutter up" in output:
            print("快门操作完成!")
            # time.sleep(1)  # 增加延时

            return True

        else:
            print("快门操作失败")
            return False

    def graceful_disconnect(self):
        """优雅地断开连接：从当前菜单逐级返回到TOP-MENU然后退出"""
        if not self.process:
            return

        try:
            print("\n正在优雅地断开连接...")

            # 如果在Shutter/Rec Operation Menu，先返回REMOTE-MENU
            print("返回REMOTE-MENU...")
            self.send_input("0")
            # time.sleep(1)

            # 从REMOTE-MENU返回TOP-MENU
            print("返回TOP-MENU...")
            self.send_input("0")
            # time.sleep(1)

            # 在TOP-MENU选择退出
            print("退出程序...")
            self.send_input("x")
            # time.sleep(1)

            # 等待程序正常退出
            self.process.wait(timeout=3)
            print("程序已正常退出")

        except subprocess.TimeoutExpired:
            print("等待程序退出超时，强制终止...")
            self.process.kill()
        except Exception as e:
            print(f"断开连接时出错: {e}")
            if self.process.poll() is None:
                self.process.kill()
        finally:
            self.process = None
            self.connected = False

    def disconnect(self):
        if self.process:
            try:
                # 优先使用优雅断开
                if self.connected:
                    self.graceful_disconnect()
                else:
                    # 如果未连接，直接终止
                    self.process.terminate()
                    self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            finally:
                self.process = None
                self.connected = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


if __name__ == "__main__":
    # 基本使用示例
    with SonyCameraController() as camera:
        if camera.connect_camera(1):
            if camera.navigate_to_shutter():
                success, files = camera.take_photo()
                if success:
                    print(f"\n拍照成功! 生成文件: {files}")
                else:
                    print("\n拍照失败")
            else:
                print("\n无法进入快门菜单")
        else:
            print("\n相机连接失败")
