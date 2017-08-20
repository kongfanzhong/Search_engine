import os
filename=open('hadoop/data/map_reduce_input_data','r')
num_lines = sum(1 for line in filename)
print("nums of line is",num_lines)
filename.close()
path='hadoop/mapreduce/input/'

if os.path.exists(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            os.remove(os.path.join(root,name))
    os.rmdir(path)
os.mkdir(path)
index=1
f1=open("hadoop/mapreduce/input/file_0","w")
i=1
with open("hadoop/data/map_reduce_input_data","r") as bigfile:
    for line in bigfile.readlines():
        
        if index==331:
            index=1
            f1.close()
            f1=open("hadoop/mapreduce/input/file_"+str(i),"w")
            i=i+1
        f1.write(line)
        index=index+1
f1.close()


        

