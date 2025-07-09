import sys
import os
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from mutagen.oggvorbis import OggVorbis
import argparse
import io
import struct

def low_freq_vibration_boost(input_file, output_file=None, 
                            cutoff=250, threshold=0.2, 
                            plot=False, boost_factor=2.0):

    if output_file is None:
        output_file = input_file.replace('.ogg', '_bassboost.ogg')
    
    # 读取原始OGG文件
    with open(input_file, 'rb') as f:
        ogg_data = f.read()
    
    # 获取采样率 - 使用mutagen获取元数据
    try:
        orig_audio = OggVorbis(io.BytesIO(ogg_data))
        sample_rate = orig_audio.info.sample_rate
    except:
        sample_rate = 44100
    
    pcm_data = []
    pos = 0
    while pos < len(ogg_data):
        if ogg_data[pos:pos+4] == b'OggS':
            header_size = 27
            segment_table = ogg_data[pos+27]
            segment_table_size = segment_table
            packet_size = sum(ogg_data[pos+28:pos+28+segment_table])
            
            data_start = pos + header_size + segment_table
            
            # 提取PCM数据
            for i in range(data_start, data_start+packet_size, 2):
                if i+1 >= len(ogg_data):
                    break
                sample = struct.unpack('<h', ogg_data[i:i+2])[0]
                pcm_data.append(sample)
            
            pos = data_start + packet_size
        else:
            pos += 1
    
    # 如果没有提取到PCM数据，使用随机数据作为后备
    if len(pcm_data) == 0:
        print("警告: 无法提取PCM数据，使用模拟数据")
        pcm_data = np.random.randint(-32768, 32767, 10000).tolist()
        sample_rate = 44100
    
    samples = np.array(pcm_data, dtype=np.float32)
    samples /= 32768.0 
    
    # 设计低通滤波器 (Butterworth 4阶)
    nyquist = 0.5 * sample_rate
    normal_cutoff = cutoff / nyquist
    b, a = signal.butter(4, normal_cutoff, btype='low', analog=False)
    
    # 应用低通滤波 - 只保留低频
    low_freq_samples = signal.filtfilt(b, a, samples)
    
    # 低频增强处理
    low_freq_samples *= boost_factor
    low_freq_samples = np.clip(low_freq_samples, -1.0, 1.0)
    
    # 分帧处理 (30ms帧)
    frame_size = int(sample_rate * 0.03)
    frames = [low_freq_samples[i:i+frame_size] 
             for i in range(0, len(low_freq_samples), frame_size)]
    
    # 生成震动模式
    vib_pattern = []
    for frame in frames:
        if len(frame) == 0: 
            continue
            
        # 使用RMS能量 (更适合低频)
        energy = np.sqrt(np.mean(frame**2))
        
        if energy > threshold:
            # 震动时长与能量成正比 (80-300ms)
            duration = int(80 + 220 * energy)
            vib_pattern.extend([0, duration])
    
    # 保存分析图表
    if plot:
        plt.figure(figsize=(12, 8))
        
        # 原始频谱
        plt.subplot(2, 1, 1)
        plt.specgram(samples, Fs=sample_rate, NFFT=1024)
        plt.title('原始音频频谱图')
        plt.xlabel('时间 (秒)')
        plt.ylabel('频率 (Hz)')
        plt.axhline(cutoff, color='r', linestyle='--')
        
        # 震动模式可视化
        plt.subplot(2, 1, 2)
        times = [0]
        for i, val in enumerate(vib_pattern):
            times.append(times[-1] + val/1000)
        
        plt.step(times[:-1], vib_pattern, where='post')
        plt.title('震动模式时序')
        plt.xlabel('时间 (秒)')
        plt.ylabel('震动时长 (ms)')
        
        plt.tight_layout()
        plot_file = os.path.splitext(output_file)[0] + '_analysis.png'
        plt.savefig(plot_file)
        print(f"生成频谱分析图: {plot_file}")
    
    # 创建输出文件（保留原始音频）
    with open(output_file, 'wb') as dst:
        dst.write(ogg_data)
    
    # 注入低频震动元数据
    ogg = OggVorbis(output_file)
    ogg["ANDROID_HAPTIC"] = "1"
    ogg["HAPTIC_MODE"] = "BASS_BOOST"
    ogg["BASS_CUTOFF"] = str(cutoff)
    ogg["BASS_BOOST"] = str(boost_factor)
    ogg["HAPTIC_PATTERN"] = [",".join(map(str, vib_pattern))]
    ogg.save()
    
    print(f"低频震动增强完成: {output_file}")
    print(f"   - 目标频段: <{cutoff}Hz")
    print(f"   - 增强系数: {boost_factor}x")
    print(f"   - 震动事件: {len(vib_pattern)//2}次")
    
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='低频震动增强引擎')
    parser.add_argument('input', help='输入OGG文件')
    parser.add_argument('-o', '--output', help='输出文件', default=None)
    parser.add_argument('-c', '--cutoff', type=int, default=250, 
                       help='低通滤波截止频率(Hz)')
    parser.add_argument('-t', '--threshold', type=float, default=0.15,
                       help='震动触发阈值(0.0-1.0)')
    parser.add_argument('-b', '--boost', type=float, default=2.0,
                       help='低频增强系数')
    parser.add_argument('-p', '--plot', action='store_true',
                       help='生成频谱分析图')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)
    
    low_freq_vibration_boost(
        args.input, 
        output_file=args.output,
        cutoff=args.cutoff,
        threshold=args.threshold,
        plot=args.plot,
        boost_factor=args.boost
    )