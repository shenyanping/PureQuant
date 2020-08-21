# talib库安装指南

```python
pip install talib
```

直接安装 不成功，因为python pip源对应的ta-lib是32位的，不能安装在64位的系统上。

所以需要使用如下方法进行安装：

在当前文件夹下，shift + 鼠标右键，选择“在此处打开PowerShell窗口”进入命令行，输入：

```python
pip install TA_Lib-0.4.18-cp37-cp37m-win_amd64.whl
```

按回车键

```python
Processing c:\users\administrator\downloads\ta_lib-0.4.18-cp37-cp37m-win_amd64.whl
Installing collected packages: TA-Lib
Successfully installed TA-Lib-0.4.18
```

如显示“Successfully installed TA-Lib-0.4.18”则安装成功。