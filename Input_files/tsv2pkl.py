#When eigenvec or tsv are converted to PKL, the PANDAS version and model version should be the same as DNNGP.
#So, please run the program in a DNNGP environment.
import pandas as pd
########Set path section
inpath=r"C:\Users\Cloud\Desktop\ai_homework\data\Maize_SelfingPrediction_Example\new_test\snp\snp.eigenvec" #Set input path
outpath=r"C:\Users\Cloud\Desktop\ai_homework\data\Maize_SelfingPrediction_Example\new_test\snp\maize1k.train.pkl" #Set output path

########Conversion format section
inpath=inpath.replace('\\','/') #Replace '\' with '/' in the input path.
outpath=outpath.replace('\\','/') #Replace '\' with '/' in the output path.
if "eigenvec" in inpath:
    # 先读取文件检查结构
    Gene = pd.read_csv(inpath, sep='\t', header=0)
    
    # 如果第一列是#FID，第二列是#IID或IID，使用第二列作为index
    if '#FID' in Gene.columns or Gene.columns[0] == '#FID':
        Gene = pd.read_csv(inpath, sep='\t', header=0, index_col=1)
        if '#FID' in Gene.columns:
            del Gene['#FID']
    # 如果第一列是#IID或IID，使用第一列作为index
    elif '#IID' in Gene.columns or 'IID' in Gene.columns or Gene.columns[0] in ['#IID', 'IID']:
        Gene = pd.read_csv(inpath, sep='\t', header=0, index_col=0)
    else:
        # 默认使用第一列作为index
        Gene = pd.read_csv(inpath, sep='\t', header=0, index_col=0)
    
    Gene.to_pickle(outpath) #output pkl file
elif "csv" in inpath:
    Gene = pd.read_csv(inpath, sep=',',header=0,index_col=0) #read csv file.
    Gene.to_pickle(outpath) #output pkl file
else:
    Gene = pd.read_csv(inpath, sep='\t',header=0,index_col=0) #read tsv file.
    Gene.to_pickle(outpath) #output pkl file
