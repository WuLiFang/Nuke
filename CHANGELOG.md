# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.20.7](https://github.com/WuLiFang/Nuke/compare/v0.20.6...v0.20.7) (2020-07-29)


### Features

* add third party node FilmicTonemappingOperator ([b83f142](https://github.com/WuLiFang/Nuke/commit/b83f142c46c2376286d4657f62788dbb003dbae0))
* arnold precomp ([5edd665](https://github.com/WuLiFang/Nuke/commit/5edd665c041d3c4e6d35e7242cae87691b1fd3e3))
* **RoateCrop:** v0.1.0 add new node ([54cec0f](https://github.com/WuLiFang/Nuke/commit/54cec0f0f5b0a281ebc470ad3135ae8dc11232cc))
* **SoftGlow:** v0.1.2 add width channel knob ([4194084](https://github.com/WuLiFang/Nuke/commit/4194084f5757993d413b699b4abe367e702b0507))
* **SoftGlow:** v0.1.3 skip glow that size less than 1 ([0303209](https://github.com/WuLiFang/Nuke/commit/03032095aca1af311a9015b6c86a77016e656fdd))


### Bug Fixes

* **SoftGlow:** v0.1.4 should always use default input ([cb61203](https://github.com/WuLiFang/Nuke/commit/cb612037bff924d399e02df770f945504dc0dcb4))

### [0.20.6](https://github.com/WuLiFang/Nuke/compare/v0.20.5...v0.20.6) (2020-07-05)


### Features

* update expire time to 2021-07-01 ([c56d413](https://github.com/WuLiFang/Nuke/commit/c56d413470211686c5ead85019ace23fcf301db0))
* **SoftGlow:** v0.1.1 add more knobs ([bf249b6](https://github.com/WuLiFang/Nuke/commit/bf249b63f6d23ba42aa8a74a5f0957c26ef97c7c))
* add message for no selected node ([c4c8002](https://github.com/WuLiFang/Nuke/commit/c4c80023a35339a558542641a71763a7fca35760))
* add OnionSkin node ([f47a6ef](https://github.com/WuLiFang/Nuke/commit/f47a6efeffb0c3fd457c198cad71d360bed219a8))
* add SoftGlow node ([c1e8643](https://github.com/WuLiFang/Nuke/commit/c1e8643d447f7b0d90acf92bce3f8174a3d9c188))
* **OnionSkin:** 0.1.2 add effect_only knob ([09ccb1b](https://github.com/WuLiFang/Nuke/commit/09ccb1bca0c53c49d857249ccf541c1862779573))
* add OnionSkin.knob_hash to invalidate viewer cache ([979614d](https://github.com/WuLiFang/Nuke/commit/979614dacef9e97ab96803a2decca3b6ee826882))
* add rotopaint dopesheet ([0e8dc18](https://github.com/WuLiFang/Nuke/commit/0e8dc1836bea1e5ac567d5fcc8a7ac6526e3d12a))


### Bug Fixes

* active pyblish panel remains tab unchanged ([012b652](https://github.com/WuLiFang/Nuke/commit/012b652945060a765bb55edad3e26f5e01213af6))
* avoid use nuke.openPanels() ([b9604bf](https://github.com/WuLiFang/Nuke/commit/b9604bf853573b9e9cbeb8cb5eba1248f1fa9372))
* pyblish window can not active if window deleted ([bd2c950](https://github.com/WuLiFang/Nuke/commit/bd2c950182b1add1f3a9045f53ee6cb5061c2e47))
* **OnionSkin:** 0.1.1 wrong result when frame out of range ([f88e9e9](https://github.com/WuLiFang/Nuke/commit/f88e9e98a28defd835de5ad4f59fcefa343b402d))
* active viewer input when no input ([eed6775](https://github.com/WuLiFang/Nuke/commit/eed6775b0686717743d92c45501793e57d90c959))
* handle overlap frame for rotopaint dopesheet ([fc3439f](https://github.com/WuLiFang/Nuke/commit/fc3439fbe91069441a558ded9fc733650cb64f76))
* unexpected transition when using rotopaint dopesheet ([2d58e21](https://github.com/WuLiFang/Nuke/commit/2d58e212233cc505955bb2f89ae7e1a9a77ce45e))

### [0.20.5](https://github.com/WuLiFang/Nuke/compare/v0.20.4...v0.20.5) (2020-05-19)


### Features

* add more prefix filter ([c8bc545](https://github.com/WuLiFang/Nuke/commit/c8bc54526aa6e387f6a93847d135baf2c676cc8f))
* update expire time to 2021-01-01 ([d79a95c](https://github.com/WuLiFang/Nuke/commit/d79a95c22ec92f4da0ee923240d8f6e3527ef5e1))
* **wlf_Lightwrap:** add channels control ([7f5a71d](https://github.com/WuLiFang/Nuke/commit/7f5a71d51881b01d65d4682ff963f4544e7c9dcb))


### Bug Fixes

* **deps:** update dependency jinja2 to v2.11.0 ([6f3ff93](https://github.com/WuLiFang/Nuke/commit/6f3ff93e9c8d9e4d4a4817eecd44f63664db1bdf))
* **wlf_Lightwrap:** blur on rgba channel instead of rgb channel ([a336040](https://github.com/WuLiFang/Nuke/commit/a33604093cdff9c609da9ca04fbcbec3304b2c30))

### [0.20.4](https://github.com/WuLiFang/Nuke/compare/v0.20.3...v0.20.4) (2020-01-10)

### Features

- **DirectionLightKeyer:** add axis input (v0.5.0) ([e6b765b](https://github.com/WuLiFang/Nuke/commit/e6b765b2449fcd57d25196bf2eb52d8eac52fd1e))
- add `GenerateVector` plug-in ([13e9f4e](https://github.com/WuLiFang/Nuke/commit/13e9f4eb1e273f35f69f63fb24945c6579d87a3e))
- **script-use-seq:** add html report ([55af938](https://github.com/WuLiFang/Nuke/commit/55af938bdfe5c0986e8fbdbe57d9ce01ced06550))
- add `WeightedErode` node ([91e496b](https://github.com/WuLiFang/Nuke/commit/91e496b8e2e333f97bbf856b6d506afa07fe0717))
- add script use seq ([01872c1](https://github.com/WuLiFang/Nuke/commit/01872c1332c450c5bbb56b2215b37d980338cd0e))
- improve dialog for match drop frame ([ccc556d](https://github.com/WuLiFang/Nuke/commit/ccc556dcd121296db9efe317d212a6e79008d45c))
- modify bbox for `GenerateVector` ([a280f98](https://github.com/WuLiFang/Nuke/commit/a280f981a7c9109f200dc841aae8710d7ee6c5a4))
- support match drop frame ([9354576](https://github.com/WuLiFang/Nuke/commit/9354576a83d09c9a1e6d8ca2bb0ab1b066693aa6))
- update expire time to 2020-07-01 ([aee05f0](https://github.com/WuLiFang/Nuke/commit/aee05f0df14e29e5722a59868c6ce4e67f7ea090))

### Bug Fixes

- asset monitor cause crash ([0504a29](https://github.com/WuLiFang/Nuke/commit/0504a2917f26c5a12fc7d84d7ba5309aaaa89cc6))
- autolabel cause lag when has many asset ([a936c36](https://github.com/WuLiFang/Nuke/commit/a936c3681f76dad83f7e9cc336e6923558239f64))
- console encoding issue on windows ([ad718c2](https://github.com/WuLiFang/Nuke/commit/ad718c2b3345b3ee92c33de81f86032305eab9d3))
- move wlf driver mapping to other plugin ([6a5f1ee](https://github.com/WuLiFang/Nuke/commit/6a5f1ee713a999f2eed22ff78d43e0b7726ef849))
- unicode error when validation setup ([3b25782](https://github.com/WuLiFang/Nuke/commit/3b25782b4af69cb64848cac22530d401a70cecd3))
- **deps:** update dependency `cgtwq` ([d3d5cb0](https://github.com/WuLiFang/Nuke/commit/d3d5cb0e004bbf8da44db6fdab29097deac91c42))
- **script-use-seq:** fix batch mode ([33ecf76](https://github.com/WuLiFang/Nuke/commit/33ecf763c5b40dae9f3022a5bc0b4c6e46110b08))
- **script-use-seq:** should search nk file recursive ([3b2b364](https://github.com/WuLiFang/Nuke/commit/3b2b364d6bdb1126bea729b1112ca158c6c78bd1))

## [0.20.3](https://github.com/WuLiFang/Nuke/compare/v0.20.2...v0.20.3) (2019-07-02)

### Chore

- update expire date to 2020-01-01

## [0.20.2](https://github.com/WuLiFang/Nuke/compare/v0.20.1...v0.20.2) (2019-05-23)

### Bug Fixes

- cgtw ws connection issue ([863625e](https://github.com/WuLiFang/Nuke/commit/863625e))

### Build System

- add Makefile ([ae065b9](https://github.com/WuLiFang/Nuke/commit/ae065b9))

## 0.20.1 (2019-05-11)

### Bug Fixes

- **wlf_Write:** render png from exr ([e79c85b](https://github.com/WuLiFang/Nuke/commit/e79c85b))
- IOError[0] on windows 10 when launch ([1ac29c3](https://github.com/WuLiFang/Nuke/commit/1ac29c3))

### Build System

- correct docs build ([5fe318f](https://github.com/WuLiFang/Nuke/commit/5fe318f))

## 0.20.0 (2019-02-20)

## 0.19.2 (2019-01-02)

## 0.19.1 (2018-09-26)

## 0.19.0 (2018-08-17)

## 0.18.0 (2018-08-16)

## 0.17.0 (2018-08-15)

## 0.16.2 (2018-08-14)

## 0.16.1 (2018-08-13)

## 0.16.0 (2018-08-13)

## 0.15.4 (2018-08-08)

## 0.15.3 (2018-08-07)

## 0.15.2 (2018-08-03)

## 0.15.1 (2018-08-03)

## 0.15.0 (2018-08-03)

## 0.14.2 (2018-08-02)

## 0.14.1 (2018-07-27)

## 0.14.0 (2018-07-27)

## 0.13.0 (2018-07-25)

## 0.12.0 (2018-07-24)

## 0.10.2 (2018-07-17)

## 0.10.0 (2018-07-16)

## 0.9.3 (2018-07-16)

## 0.9.2 (2018-07-12)

## 0.9.1 (2018-07-11)

## 0.9.0 (2018-07-11)

## 0.8.0 (2018-07-05)

## 0.7.3 (2018-06-29)

## 0.7.2 (2018-06-27)

## 0.7.1 (2018-06-26)

## 0.7.0 (2018-06-26)

## 0.6.4 (2018-06-13)

## 0.6.3 (2018-04-26)

## 0.6.1 (2018-04-19)

## 0.5.4 (2018-04-02)

## 0.5.3 (2018-04-02)

## 0.5.2 (2018-04-02)

## 0.5.1 (2018-03-29)

## 0.5.0 (2018-03-29)

## 0.4.24 (2018-01-29)

## 0.4.23 (2018-01-08)

## 0.4.22 (2017-12-31)

## 0.4.20 (2017-12-22)

## 0.4.19 (2017-12-21)

## 0.4.18 (2017-12-07)

## 0.4.17 (2017-11-28)

## 0.4.16 (2017-11-23)

## 0.4.15 (2017-11-19)

## 0.4.14 (2017-11-10)

## 0.4.12 (2017-11-01)

## 0.4.11 (2017-10-24)

## 0.4.10 (2017-10-21)

## 0.4.9 (2017-10-18)

## 0.4.8 (2017-10-18)

## 0.4.6 (2017-10-12)

## 0.4.5 (2017-10-10)

## 0.4.4 (2017-10-09)

## 0.4.3 (2017-10-06)

## 0.4.2 (2017-09-29)

## 0.4.1 (2017-09-25)

## 0.4.0 (2017-09-25)

## 0.3.10 (2017-09-21)

## 0.3.9 (2017-09-20)

## 0.3.8 (2017-09-19)

## 0.3.7 (2017-09-15)

## 0.3.6 (2017-09-14)

## 0.3.5 (2017-09-13)

## 0.3.4 (2017-09-11)

## 0.3.3 (2017-09-11)

## 0.3.2 (2017-09-06)

## 0.3.1 (2017-09-06)

## 0.3.0 (2017-09-05)

## 0.2.0 (2017-08-25)

## 0.1.0 (2017-08-25)
