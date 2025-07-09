此程序基于HapticAdd程序 使用低通滤波器使线性马达尽量播放低频信号以增强低音效果
目前仍处于实验中 其中BassTurboPure所滤得的低频信号比BassTurbo滤得的更纯
必须安装的依赖
 pip install pydub numpy scipy matplotlib mutagen
使用方法
 增强250Hz以下低频 (默认设置)
  python bassTurbo.py music.ogg
 增强120Hz以下低频 (适合重低音)
  python bassTurbo.py beat.ogg -c 120
 增强效果可视化
  python bassTurbo.py drum.ogg -p -b 3.0
    一定要先把音频转成48khz
然后再转换成.ogg格式文件！！！
           注:在命令符后面输入 
 -o可指定输出文件名
默认为自动生成    
 -b可设置增强倍数
默认为2.0
 -t可设置震动触发灵敏度
默认为0.15
  生成纯低频震动
   python bassTurboPure.py music.ogg
具体效果因设备而定

By YuzakiPTeam@2025
第一次这种程序 有问题请您反馈和谅解
感谢大家的支持
暂不支持小米设备（缺少相关API）
目前通过测试且效果较好的机型 一加13
项目中附带两个音频文件 其中AF为载入过元数据的样本音频 BF为没有载入过元数据的样本音频
其他机型请自行测试 所导致的问题本人概不负责