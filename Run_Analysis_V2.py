# -*- coding: utf-8 -*-
"""
Created on Sat May 24 12:51:21 2014

@author: Dakota
"""
import os
import shutil
import Song_Detection_V7

class Run_Analysis:
    
    def __init__(self):
        self.root = '/mnt/data/Mockingbird Videos'
        self.cwd = os.getcwd()
        self.input_list = []
        #Tree = raw_input('Create a file tree based from /mnt?')
        Tree = 'NO'
        Tree = Tree.upper()
        if Tree == 'YES' or Tree == 'Y':
            self.create_tree()
        #Q = raw_input("Use default input?")
        Q = 'YES'
        Q = Q.upper()
        if Q == 'YES' or Q == 'Y':
            #print Q_1
            Q_1 = "NO"
            #Q_1 = raw_input("Analyze mnt files?")
            Q_1 = Q_1.upper()
            if Q_1 == 'YES' or Q_1 == 'Y':
                head, tail = os.path.split(self.root)
                splitter = self.cwd.split(tail + '/')
                base = self.root + '/'
                wav_dir = os.path.join(base, splitter[1])
                self.get_file(wav_dir)
            else:  
                self.get_file(self.cwd)
            for i in self.input_list:
                Song_Detection_V7.run(i)
        else:
            f = raw_input("Please give a .txt input file.")
            Song_Detection_V7.run(f)


    def get_file(self, wav_dir):
        file_list = []
        self.restart_list = []
        wav_files = os.listdir(wav_dir)
        txt_files = os.listdir(self.cwd)
        for i in wav_files:
            if i.endswith('.wav'):
                splitter = i.split('.')
                file_list.append(splitter[0])
        for i in file_list:
            f = os.path.join(wav_dir, i)
            formout = i + '_FormOut.txt'
#            if 'VID' in i:
#                splitter = i.split(' ')
#                formout = splitter[1] + '_' + splitter[3] + '_FormOut.txt'
#            else:
#                formout = i + '_FormOut.txt'        
            if (i + '_input.txt') not in txt_files and formout not in txt_files and (i + '_restart.txt') not in txt_files:
                self.default_input(f)
                txt_files = os.listdir(self.cwd)
            if (i + '_input.txt') in txt_files:
                self.input_list.append(i)   
            if (i + '_restart.txt') in txt_files:
                self.default_input(f, 'True')
                self.restart_list.append(i)
            
    def default_input(self, f, restart = 'False'):
        path, name = os.path.split(f)
        out = open(name + '_input.txt', 'w')
        d_list = [('Restart', restart), ('Blocksize', '15'), ('Percentile', '0.90'), ('Lhertz', '2000'), ('Uhertz', '7000'), ('Step', '0.15'), ('Threshold', '0.10'), ('MinGap', '10'), ('namefile', f), ('fft_plot', 'False'), ('time_plot', 'False'), ('fplot', 'False')]
        for i in d_list:
            x,y = i
            out.write(x + '\t' + y + '\n')
        out.close()
        
    def bash_write(self, path, ext):
        end = '\n'
        path_split = path.split(self.root)
        new_path = "/mnt/data/Mockingbird\ Videos" + path_split[1]
        if ext == '.AVI':
            num = 1
        else:
            num = 2
        bash = open("vidcon" + str(num) + ".sh", 'w')
        bash.write("#! /bin/bash" + end)
        bash.write("for f in ls " + new_path + "/*" + ext + ';' + end)
        bash.write('do' + end)
        bash.write('s=${f##*/}' + end)
        bash.write('ffmpeg -loglevel quiet -i "${f%%.*}"' + ext + ' "${s%%.*}".wav < /dev/null;' + end)
        bash.write('python Run_Analysis_V2.py' + end)
        bash.write('done &')
        bash.close()
        
        
    def create_tree(self):
        analysis = 'Run_Analysis_V2.py'
        detection = 'Song_Detection_V7.py'
        sound = 'Sound_Analyze_V4.py'
        bash1 = 'vidcon1.sh'
        bash2 = 'vidcon2.sh'
        base,x = os.path.split(self.root)
        base = base + '/'
        for root, dirs, files in os.walk(self.root):
            splitter = root.split(base)
            new = os.path.join(self.cwd, splitter[1])
            if new != self.cwd + '/':
                os.mkdir(new)
            os.chdir(new)
            for i in files:
                if i.endswith('.AVI') or i.endswith('.wmv'):
                    file_split = i.split('.')
                    self.default_input(file_split[0])
                    if analysis not in new:
                        f1 = os.path.join(self.cwd, analysis)
                        shutil.copy(f1, new)
                    if detection not in new:
                        f2 = os.path.join(self.cwd, detection)
                        shutil.copy(f2, new)
                    if sound not in new:
                        f3 = os.path.join(self.cwd, sound)
                        shutil.copy(f3, new)
                    if bash1 not in new:
                        self.bash_write(root, '.AVI')
                    if bash2 not in new:
                        self.bash_write(root, '.wmv')
                
                
        
b = Run_Analysis()
