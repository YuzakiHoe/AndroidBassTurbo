import sys
import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from mutagen.oggvorbis import OggVorbis
import argparse
import struct
import io  # 添加缺失的io模块

def strict_low_freq_vibration(input_file, output_file=None, 
                             low_cut=20, high_cut=250, 
                             threshold=0.2, plot=False):
    """
    纯低频震动增强 - 只响应20-250Hz频段
    :param input_file: 输入OGG文件
    :param output_file: 输出OGG文件
    :param low_cut: 低频下限(Hz)
    :param high_cut: 低频上限(Hz)
    :param threshold: 震动触发阈值
    :param plot: 是否生成分析图
    """
    # 读取原始OGG文件
    with open(input_file, 'rb') as f:
        ogg_data = f.read()
    
    # 获取采样率
    try:
        orig_audio = OggVorbis(io.BytesIO(ogg_data))
        sample_rate = orig_audio.info.sample_rate
    except:
        sample_rate = 44100
    
    # 提取PCM数据
    pcm_data = []
    pos = 0
    while pos < len(ogg_data):
        if ogg_data[pos:pos+4] == b'OggS':
            header_size = 27
            segment_table = ogg_data[pos+27]
            data_start = pos + header_size + segment_table
            packet_size = sum(ogg_data[pos+28:pos+28+segment_table])
            
            # 提取16位PCM样本
            for i in range(data_start, min(data_start+packet_size, len(ogg_data)-1), 2):
                if i+1 >= len(ogg_data):
                    break  # 防止越界
                sample = struct.unpack('<h', ogg_data[i:i+2])[0]
                pcm_data.append(sample)
            
            pos = data_start + packet_size
        else:
            pos += 1
    
    if len(pcm_data) == 0:
        print("⚠️ 警告: 无法提取PCM数据，使用空数据")
        pcm_data = [0] * 44100  # 1秒静音
    samples = np.array(pcm_data, dtype=np.float32)
    samples /= 32768.0  # 归一化
    
    # 设计带通滤波器 - 只允许20-250Hz通过
    nyquist = 0.5 * sample_rate
    low = low_cut / nyquist
    high = high_cut / nyquist
    b, a = signal.butter(8, [low, high], btype='band')
    
    # 应用带通滤波 - 只保留目标低频
    low_freq_only = signal.filtfilt(b, a, samples)
    
    # 分帧处理 (40ms帧 - 更适合低频)
    frame_size = int(sample_rate * 0.04)
    frames = [low_freq_only[i:i+frame_size] 
             for i in range(0, len(low_freq_only), frame_size)]
    
    # 生成纯低频震动模式
    vib_pattern = []
    for frame in frames:
        if len(frame) == 0: 
            continue
            
        # 计算低频能量
        energy = np.sqrt(np.mean(frame**2))
        
        # 只对显著低频信号响应
        if energy > threshold:
            # 震动时长与能量成正比 (100-400ms)
            duration = int(100 + 300 * energy)
            vib_pattern.extend([0, duration])
    
    # 可视化分析
    if plot:
        plt.figure(figsize=(12, 10))
        
        # 原始频谱
        plt.subplot(3, 1, 1)
        freqs, psd = signal.welch(samples, sample_rate, nperseg=1024)
        plt.semilogy(freqs, psd)
        plt.title('原始音频频谱')
        plt.xlabel('频率 (Hz)')
        plt.ylabel('能量')
        plt.axvspan(low_cut, high_cut, color='green', alpha=0.3)
        
        # 滤波后频谱
        plt.subplot(3, 1, 2)
        freqs, psd = signal.welch(low_freq_only, sample_rate, nperseg=1024)
        plt.semilogy(freqs, psd)
        plt.title(f'纯低频频谱 ({low_cut}-{high_cut}Hz)')
        plt.xlabel('频率 (Hz)')
        plt.ylabel('能量')
        
        # 震动模式
        plt.subplot(3, 1, 3)
        times = [0]
        for val in vib_pattern:
            times.append(times[-1] + val/1000)
        
        plt.step(times[:-1], vib_pattern, where='post')
        plt.title('纯低频震动模式')
        plt.xlabel('时间 (秒)')
        plt.ylabel('震动时长 (ms)')
        plt.ylim(0, 500)
        
        plt.tight_layout()
        plot_file = os.path.splitext(input_file)[0] + '_strict_low.png'
        plt.savefig(plot_file)
        print(f"生成分析图: {plot_file}")
    
    # 创建输出文件
    if output_file is None:
        output_file = input_file.replace('.ogg', '_strictbass.ogg')
    
    with open(output_file, 'wb') as dst:
        dst.write(ogg_data)
    
    # 注入元数据
    ogg = OggVorbis(output_file)
    ogg["ANDROID_HAPTIC"] = "1"
    ogg["HAPTIC_MODE"] = "PURE_BASS"
    ogg["LOW_CUT"] = str(low_cut)
    ogg["HIGH_CUT"] = str(high_cut)
    ogg["HAPTIC_PATTERN"] = [",".join(map(str, vib_pattern))]
    ogg.save()
    
    print(f"✅ 纯低频震动增强完成: {output_file}")
    print(f"   - 目标频段: {low_cut}-{high_cut}Hz")
    print(f"   - 震动事件: {len(vib_pattern)//2}次")
    print(f"   - 高频信号完全忽略")
    
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='纯低频震动增强引擎')
    parser.add_argument('input', help='输入OGG文件')
    parser.add_argument('-o', '--output', help='输出文件', default=None)
    parser.add_argument('-l', '--low', type=int, default=20, 
                       help='低频下限(Hz)')
    parser.add_argument('-u', '--up', type=int, default=250, 
                       help='低频上限(Hz)')
    parser.add_argument('-t', '--threshold', type=float, default=0.15,
                       help='震动触发阈值(0.0-1.0)')
    parser.add_argument('-p', '--plot', action='store_true',
                       help='生成频谱分析图')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)
    
    strict_low_freq_vibration(
        args.input, 
        output_file=args.output,
        low_cut=args.low,
        high_cut=args.up,
        threshold=args.threshold,
        plot=args.plot
    )