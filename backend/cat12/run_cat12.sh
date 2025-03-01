#!/bin/bash
# 后端路径：backend/cat12/run_cat12.sh

# 输入参数
INPUT_FILE=$1
OUTPUT_DIR=$2

# 设置MATLAB环境
export MATLAB_ROOT="/usr/local/MATLAB/MATLAB_Runtime/v912"
export LD_LIBRARY_PATH=${MATLAB_ROOT}/runtime/glnxa64:${MATLAB_ROOT}/bin/glnxa64:${LD_LIBRARY_PATH}

# 调用MATLAB编译的CAT12组件
/opt/cat12/scripts/cat12_batch_processing $INPUT_FILE $OUTPUT_DIR

# 生成伪影示例（实际需替换为真实处理）
mkdir -p $OUTPUT_DIR
cp $INPUT_FILE $OUTPUT_DIR/processed_$(basename $INPUT_FILE)
echo "CAT12 processing completed" > $OUTPUT_DIR/report.txt