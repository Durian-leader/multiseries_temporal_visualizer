#!/usr/bin/env python3
"""
基线矫正工作流程示例

此脚本演示如何在数据处理流程中使用新的基线矫正步骤。
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """运行命令并处理输出"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ 成功完成")
            if result.stdout:
                print("输出:")
                print(result.stdout)
        else:
            print("✗ 执行失败")
            if result.stderr:
                print("错误:")
                print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ 执行异常: {e}")
        return False
    
    return True

def main():
    """主函数 - 演示完整的数据处理流程"""
    
    print("基线矫正数据处理流程示例")
    print("=" * 60)
    
    # 定义工作目录
    base_dir = Path(__file__).parent
    
    # 示例数据路径（需要根据实际情况调整）
    raw_data_dir = "原始数据文件夹"  # 用户需要替换为实际路径
    step1_output = "output/step1_csv_files"  # 00select_start_idx.py的输出
    baseline_corrected_output = "output/baseline_corrected_csv"  # 基线矫正后的输出
    final_npz_output = "output/final_processed_data"  # 最终NPZ文件输出
    
    print(f"工作目录: {base_dir}")
    print(f"假设数据路径:")
    print(f"  - 原始数据: {raw_data_dir}")
    print(f"  - Step 1输出: {step1_output}")
    print(f"  - 基线矫正输出: {baseline_corrected_output}")
    print(f"  - 最终输出: {final_npz_output}")
    
    # 步骤1：选择起始索引（假设已完成）
    print(f"\n步骤 1: 选择起始索引")
    print(f"假设已经运行了 00select_start_idx.py")
    print(f"输出CSV文件应该在: {step1_output}")
    
    # 检查Step 1输出是否存在
    step1_path = Path(step1_output)
    if not step1_path.exists():
        print(f"⚠ 注意: {step1_output} 不存在")
        print("请先运行 00select_start_idx.py 生成CSV文件")
        print("\n示例命令:")
        print("python python_数据预处理与可视化/00select_start_idx.py")
        return
    
    # 步骤1.5：基线矫正
    print(f"\n步骤 1.5: 基线矫正")
    
    # 创建输出目录
    baseline_output_path = Path(baseline_corrected_output)
    baseline_output_path.mkdir(parents=True, exist_ok=True)
    
    # 选择处理模式
    print("\n请选择基线矫正模式:")
    print("1. 自动模式 (使用首末点连线)")
    print("2. 手动模式 (GUI选择基线点)")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            # 自动模式
            cmd = f"python python_数据预处理与可视化/00_5_manual_baseline_correction.py -i {step1_output} -o {baseline_corrected_output} -a -v"
            if not run_command(cmd, "自动基线矫正"):
                return
                
        elif choice == "2":
            # 手动模式
            cmd = f"python python_数据预处理与可视化/00_5_manual_baseline_correction.py -i {step1_output} -o {baseline_corrected_output} -m -v"
            print("注意: 手动模式将为每个CSV文件打开GUI工具")
            input("按 Enter 键继续...")
            if not run_command(cmd, "手动基线矫正"):
                return
        else:
            print("无效选择，退出")
            return
            
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return
    
    # 步骤2：生成NPZ数据
    print(f"\n步骤 2: 生成处理后的NPZ数据")
    
    # 创建最终输出目录
    final_output_path = Path(final_npz_output)
    final_output_path.mkdir(parents=True, exist_ok=True)
    
    # 运行01csv2npz.py（使用基线矫正后的CSV文件）
    cmd = f"python python_数据预处理与可视化/01csv2npz.py"
    print(f"注意: 需要确保01csv2npz.py使用 {baseline_corrected_output} 作为输入")
    
    if not run_command(cmd, "生成NPZ数据文件"):
        return
    
    # 步骤3：转换为MATLAB格式
    print(f"\n步骤 3: 转换为MATLAB格式")
    cmd = "python npz_to_mat.py"
    if not run_command(cmd, "转换为MATLAB格式"):
        return
    
    print(f"\n{'='*60}")
    print("✓ 数据处理流程完成！")
    print(f"✓ 基线矫正后的CSV文件: {baseline_corrected_output}")
    print(f"✓ 现在可以使用MATLAB脚本进行可视化")
    print("✓ 建议运行的MATLAB脚本:")
    print("  - main01_3d.m")
    print("  - main02_heatmap.m") 
    print("  - main03_heatmapwithprofile.m")
    print('='*60)

if __name__ == "__main__":
    main()