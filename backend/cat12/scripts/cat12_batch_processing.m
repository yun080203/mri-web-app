% 后端路径：backend/cat12/scripts/cat12_batch_processing.m
function cat12_batch_processing(input_file, output_dir)
    % 初始化CAT12配置
    cat12_dir = '/opt/cat12';
    addpath(fullfile(cat12_dir, 'spm12'));
    addpath(fullfile(cat12_dir, 'cat12'));
    
    % 创建批处理作业
    matlabbatch{1}.spm.tools.cat.estwrite.data = {input_file};
    matlabbatch{1}.spm.tools.cat.estwrite.opts.ngaus = [2 2 2 4]; % 组织分类参数
    matlabbatch{1}.spm.tools.cat.estwrite.output.surface = 0; % 关闭表面重建
    
    % 运行处理
    spm('defaults', 'PET');
    spm_jobman('run', matlabbatch);
    
    % 移动结果文件
    movefile('mri/*', output_dir);
end