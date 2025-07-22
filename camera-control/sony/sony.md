# 使用 Sony Camera Remote SDK 的例程遥控拍摄

使用命令行工具调用 Sony CRSDK 中的例程，连接相机、触发快门（同时会回传图片）和断开连接。

另附一个 PyQt 版的简易 UI。

## 已知问题

有概率显示了触发快门，但实际上没有拍照也没有回传。将一切都设置成手动（对焦、白平衡、曝光）会好一些。

## 目的

windows 上无法使用 gphoto2，索尼也没有别的靠谱的第三方库来遥控相机。

基于 CRSDK 的 python 绑定还在研究中，先用这个临时使用一下。

## Macos

如果使用的是 mac 或 linux，可以直接用 gphoto2。

## 例程 APP

搭配的例程 APP 打包放在 [Google Drive](https://drive.google.com/file/d/1w5s4aaw86XeyJTFuAab0dnqqlC9BCFwo/view?usp=sharing)，使用的时候需要解压，把 Debug 文件夹整个和 py 放在一起。


