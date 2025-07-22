Remote SDK version: 2.0.00
Initialize Remote SDK...
Working directory: "C:\\Users\\Jackc\\Desktop\\python-sony-camera\\Debug"
Remote SDK successfully initialized.

Enumerate connected camera devices...
Camera enumeration successful. 1 detected.

[1] ZV-E10M2 (D18D507473D4)

Connect to camera with input number...
input>

按下按键 1 并回车：

Connect to selected camera...
Create camera SDK camera callback object.
Release enumerated camera list.
<< TOP-MENU >>
What would you like to do? Enter the corresponding number.
(1) Connect (Remote Control Mode)
(2) Connect (Contents Transfer Mode)
(3) Connect (Remote Transfer Mode)
(x) Exit
input>

按下按键 1 并回车：

C:\Users\Jackc\Desktop\python-sony-camera\Debug
Remote Control Mode
<< REMOTE-MENU >>
What would you like to do? Enter the corresponding number.
(s) Status display and camera switching
(0) Disconnect and return to the top menu
(1) Shutter/Rec Operation Menu
(2) Shooting Menu
(3) Exposure/Color Menu
(4) Focus Menu
(5) Setup Menu
(6) Contents Operation Menu
(7) Other Menu
input> Connected to ZV-E10M2 (D18D507473D4)

有概率会变成：

C:\Users\Jackc\Desktop\python-sony-camera\Debug
Remote Control Mode
<< REMOTE-MENU >>
What would you like to do? Enter the corresponding number.
(s) Status display and camera switching
(0) Disconnect and return to the top menu
(1) Shutter/Rec Operation Menu
(2) Shooting Menu
(3) Exposure/Color Menu
(4) Focus Menu
(5) Setup Menu
(6) Contents Operation Menu
(7) Other Menu
input>
[CAT: Connect   ] [DETAILS: A connection failed because camera was not ready]
ZV-E10M2 (D18D507473D4)
Please input '0' to return to the TOP-MENU

此时需要按 0 并回车，回到上层，再按 1 重试。

正确进入菜单后：

按下按键 1 并回车：

Capture image...
Shutter down
Shutter up

<< Shutter/Rec Operation Menu >>
What would you like to do? Enter the corresponding number.
(0) Return to REMOTE-MENU
(1) Shutter Release
(2) Shutter Half Release in AF mode
(3) Shutter Half and Full Release in AF mode
(4) Continuous Shooting
(5) Focus Bracket Shot
(6) Movie Rec Button
(7) Movie Rec Button(Toggle)
input> OnWarning:Captured_Event
Complete download. File: C:\Users\Jackc\Desktop\python-sony-camera\Debug\DSC00001.ARW

这样就拍下了一张照片，同时这个 ARW 会自动传到目录下。

还可以继续按 1 并回车：

Capture image...
Shutter down
Shutter up

<< Shutter/Rec Operation Menu >>
What would you like to do? Enter the corresponding number.
(0) Return to REMOTE-MENU
(1) Shutter Release
(2) Shutter Half Release in AF mode
(3) Shutter Half and Full Release in AF mode
(4) Continuous Shooting
(5) Focus Bracket Shot
(6) Movie Rec Button
(7) Movie Rec Button(Toggle)
input> OnWarning:Captured_Event
Complete download. File: C:\Users\Jackc\Desktop\python-sony-camera\Debug\DSC00002.ARW

