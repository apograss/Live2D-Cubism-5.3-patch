# Live2D Cubism 5.3 授权绕过 — 复现教程

## 文件清单

```
reproduce/
├── README.md          ← 本文件
├── patch_rlm_v6.py    ← Python 补丁脚本
├── install.bat        ← 一键安装
└── uninstall.bat      ← 一键还原
```

## 前置条件

- ✅ Live2D Cubism 5.3 已安装（默认路径 `D:\Live2D Cubism 5.3`）
- ✅ Python 3 已安装并加入 PATH
- ✅ 原版 `.lic` 文件存在于 `C:\ProgramData\Live2D\Cubism License\12\`

> **注意**：`.lic` 文件**不需要任何修改**，使用原版即可。

---

## 方式一：一键安装（推荐）

直接**右键以管理员身份运行** `install.bat`，脚本会自动完成以下操作：

1. 在 `app/` 下创建影子目录 `dll64_crack`
2. 复制原版 DLL 到影子目录并自动打补丁
3. 修改 `CubismEditor5.bat` 的加载路径

完成后直接运行 `CubismEditor5.bat` 即可。

---

## 方式二：手动安装

### 第 1 步：创建影子目录

```powershell
mkdir "D:\Live2D Cubism 5.3\app\dll64_crack"
```

### 第 2 步：复制原版 DLL

```powershell
copy "D:\Live2D Cubism 5.3\app\dll64\rlm1603.dll" "D:\Live2D Cubism 5.3\app\dll64_crack\rlm1603.dll"
```

### 第 3 步：打补丁

```powershell
python patch_rlm_v6.py "D:\Live2D Cubism 5.3\app\dll64_crack\rlm1603.dll"
```

看到以下输出即成功：
```
  [+] ...rlmCheckout -> return 0
  [+] ...rlmCheckoutProduct -> return 0
  [+] ...rlmLicenseStat -> return 0
  [+] ...rlmStat -> return 0
  [+] ...rlmAuthCheck -> return 0
  [+] ...rlmLicenseExpDays -> return 9999
  Done! 6 functions patched.
```

### 第 4 步：修改启动脚本

用记事本打开 `D:\Live2D Cubism 5.3\CubismEditor5.bat`，找到这一行：

```
set NATIVE_PATH=app\dll64;app\dll64\windows-amd64
```

在 `app\dll64;` 前面加上 `app\dll64_crack;`，改成：

```
set NATIVE_PATH=app\dll64_crack;app\dll64;app\dll64\windows-amd64
```

保存关闭。

### 第 5 步：启动

双击 `CubismEditor5.bat`。

---

## 验证成功

标题栏显示：

```
Live2D Cubism Editor 5.3.01 [试用版 剩余 9999 天]
```

弹窗提示 `试用期剩余 9999 天`，点击 `继续使用` 即可正常使用。

---

## 还原

运行 `uninstall.bat`，或手动执行：

```powershell
rmdir /s /q "D:\Live2D Cubism 5.3\app\dll64_crack"
copy /y "D:\Live2D Cubism 5.3\CubismEditor5.bat.bak" "D:\Live2D Cubism 5.3\CubismEditor5.bat"
```

---

## 原理简述

1. **为什么不直接改原版 DLL？**
   Java 层会校验 `app/dll64/rlm1603.dll` 的文件哈希。改一个字节就崩。

2. **影子目录是怎么回事？**
   `CubismEditor5.bat` 通过 `-Djava.library.path` 指定 DLL 搜索路径。
   我们把补丁版 DLL 放在优先级更高的目录，Java 就会先加载它。
   而哈希校验读的是原版位置的文件，互不干扰。

3. **补丁改了什么？**
   6 个 JNI 函数的入口被替换为 `mov eax, N; ret`（各 6 字节）：
   - `rlmCheckout` → 返回 0（成功）
   - `rlmLicenseExpDays` → 返回 9999（天）
   - 其余 4 个状态函数 → 返回 0（正常）

4. **为什么不改 .lic？**
   原版 `.lic` 的数字签名是有效的。RLM 引擎能正常解析并填充全部字段。
   我们只欺骗"是否成功"和"剩余天数"两个返回值。
