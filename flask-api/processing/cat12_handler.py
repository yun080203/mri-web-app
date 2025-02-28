import subprocess
import os
from datetime import datetime

CAT12_PATH = '/opt/cat12/run_cat12.sh'  # Docker容器内路径

def process_mri(input_path):
    output_dir = os.path.join(
        os.path.dirname(input_path),
        'processed',
        datetime.now().strftime("%Y%m%d%H%M%S")
    )
    os.makedirs(output_dir, exist_ok=True)

    # 执行CAT12处理
    try:
        subprocess.run(
            [CAT12_PATH, '-i', input_path, '-o', output_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return {
            'status': 'success',
            'output_dir': output_dir,
            'processed_img': os.path.join(output_dir, 'mri_processed.nii')
        }
    except subprocess.CalledProcessError as e:
        return {
            'status': 'error',
            'message': e.stderr.decode()
        }