**直接可用（仅需电机+IMU，不依赖外部传感器）**

* is\_terminated
* ang\_vel\_xy\_l2
* flat\_orientation\_l2
* upward
* heading\_alignment
* joint\_torques\_l2
* joint\_vel\_l2
* joint\_acc\_l2
* joint\_pos\_limits
* joint\_vel\_limits
* joint\_power
* stand\_still
* joint\_pos\_penalty
* joint\_mirror
* action\_mirror
* action\_sync
* applied\_torque\_limits
* action\_rate\_l2

关键依据:

* 姿态相关都基于 projected\_gravity 或角速度，例如 [rewards.py**:781**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:652**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:792**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。
* 关节/动作相关都来自关节状态和动作历史，例如 [rewards.py**:81**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:107**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:300**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。

**有条件可用（需要状态估计，不是纯原始IMU电机）**

* track\_lin\_vel\_xy\_exp
* track\_ang\_vel\_z\_exp
* lin\_vel\_z\_l2
* body\_lin\_acc\_l2
* base\_height\_l2（即便 sensor\_cfg=None）
* base\_height\_hold\_time\_bonus（即便 sensor\_cfg=None）

原因:

* 速度跟踪和 z 速度惩罚依赖 base 速度项，如 [rewards.py**:22**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:38**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:736**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。
* 高度项依赖世界系 base 高度 root\_pos\_w z，如 [rewards.py**:660**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:691**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。
* 这类在仿真里有“真值”，上真实机器人时需要额外状态估计器。

**不可用（明确依赖接触/地形传感器）**

* wheel\_vel\_penalty
* undesired\_contacts
* non\_foot\_ground\_contact
* contact\_forces
* feet\_air\_time
* feet\_air\_time\_variance
* feet\_gait
* feet\_contact
* feet\_contact\_without\_cmd
* feet\_all\_contact\_hold\_without\_cmd
* feet\_stumble
* feet\_slide

关键依据:

* 都显式用到 ContactSensor 或 sensor\_cfg，如 [rewards.py**:132**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:359**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)、[rewards.py**:754**](vscode-file://vscode-app/usr/share/code/resources/app/out/vs/code/electron-browser/workbench/workbench.html)。
