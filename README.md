# 吾立方 Nuke 插件

支持 Nuke 版本：

- [x] Nuke10.0
- [x] Nuke10.5
- [x] Nuke11
- [x] Nuke12
- [x] Nuke13
- [ ] Nuke14

## 注意事项

Nuke12 以下内置是 python2，对中文支持很烂。如果处理中文路径时报错请尝试换成纯英文路径再试。

安装也不要安装在中文路径下，安装脚本暂时还不能保证正确处理中文编码。

## 使用

去[发布页面]下载压缩包

## 使用方法

- Windows

  运行 `安装.cmd` 后即可在 Nuke 中使用

## 开发

### 安装依赖

利用 GNU Make 搭建开发环境

Makefile 使用的环境变量:

NUKE_PYTHON

本机 Nuke 内置 python 路径。

PYTHON27

python2.7 路径，用于安装依赖，推荐使用最新版。
因为 Nuke 内置 python 太老了，不能使用 pip + https。

```shell
export NUKE_PYTHON="C:\Program Files\Nuke11.3v3\python.exe"
make
```

替换 `"C:\Program Files\Nuke11.3v3\python.exe"` 路径为你 Nuke 附带 python 的路径

### 测试

```shell
make test
```

## NO LICENSE 版权保留

吾立方内部使用, 其他人使用需先联系获取授权

[项目主页](https://github.com/WuLiFang/Nuke)

[发布页面]: https://github.com/WuLiFang/Nuke/releases
