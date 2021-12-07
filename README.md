# 吾立方 Nuke 插件

支持 Nuke 版本：

- [x] Nuke10.0
- [x] Nuke10.5
- [x] Nuke11
- [ ] Nuke12

## 注意事项

Nuke 内置是 python2，对中文支持很烂。如果处理中文路径时报错请尝试换成纯英文路径再试。

安装也不要安装在中文路径下，安装脚本暂时还不能保证正确处理中文编码。

## 使用

去[发布页面]下载压缩包

## 使用方法

- Windows

  运行 `安装.cmd` 后即可在 Nuke 中使用

## 开发

### 安装依赖

为使用 Nuke 的库, 需添加 nuke.pth 到 .venv/lib/site-packages 下:

```shell
export NUKE_PYTHON="C:\Program Files\Nuke11.3v3\python.exe"
make
```

替换 `"C:\Program Files\Nuke11.3v3\python.exe"` 路径为你 Nuke 附带 python 的路径

### 更新文档

文档位于 [docs](https://github.com/WuLiFang/Nuke/tree/docs) 分支, 使用 git worktree 来管理:

```shell
make docs/_build/html
```

## NO LICENSE 版权保留

吾立方内部使用, 其他人使用需先联系获取授权

[项目主页](https://github.com/WuLiFang/Nuke)

[发布页面]: https://github.com/WuLiFang/Nuke/releases
