# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 13:01:49 2013

@author: dakotahawkins
"""
import wave
import numpy
import struct
import Sound_Analyze_V4
import os 
import time
import shutil

class Restart:
    
    def __init__(self, f):
        '''
        Checks if a restart occurred, then asks user for .wav file to be analyzed. Creates necessary file names and initialized varables
        '''
        self.raw = f
        self.input = f + '_input.txt'
        self.time_1  = time.clock()
            
        restart = self.get_input()
        
        if restart == 'TRUE':
            self.run_restart()
        else:
            self.start_index = 0 #The first posistion in self.numfile to be analyzed
            self.count = 0 #The number of times the program has run
            out = open(self.output, 'w') #creates and closes an output file. Allows use of the appending function in Song_Detection
            out.close()
            self.read_Wav()
            self.restart_write()
            self.format_output()
            self.delete_file()

    def get_input(self):
        inputfile = open(self.input, 'r')
        input_list = []
        for i in range(12):
            line = inputfile.readline()
            lineS = line.split('\t')
            lineS1 = lineS[1].split('\n')
            input_list.append(lineS1[0])
        inputfile.close()
        
        restart = str(input_list[0]).upper()
        self.Blocksize = float(input_list[1])
        self.percentile = float(input_list[2])
        self.lhertz = float(input_list[3])
        self.uhertz = float(input_list[4])
        self.step = float(input_list[5])
        self.threshold = float(input_list[6])
        self.mingap = float(input_list[7])
        path = str(input_list[8])
        self.fft_Q = str(input_list[9]).upper()
        self.time_Q = str(input_list[10]).upper()
        self.filt_Q = str(input_list[11]).upper()
        
        self.wav_file = path + ".wav" #The .wav file to be analyzed
        self.output = self.raw + "_output.txt" #A .txt file with time stamps of intrest
        self.restart_file = self.raw + "_restart.txt" #file to be read given a necessary restart. File is updated everytime Song_Detection is called.
        
        if self.fft_Q == "TRUE":
            fft_namefile = self.raw + "_fftdata.txt"
            out = open(fft_namefile, 'w')
            out.close()
            
        if self.time_Q == "TRUE":
            time_out = self.raw + "_timedata.txt"
            out = open(time_out, 'w')
            out.close()
        
        if self.filt_Q == "TRUE":
            f_out = self.raw + "_ftimedata.txt"
            out = open(f_out, 'w')
            out.close()
        
        return restart
    
    def get_average(self, wav, nchannels):
        '''
        Module that randomly selects a minute in the recording. The average
        amplitude of that minute will then be used as the "silence" value and
        will be used to calculate decibels later.
        '''
        if self.length > 60 * self.fs:
            start = int(numpy.random.uniform(0, self.length - 60*self.fs))
            wav.setpos(start)
            sound = self.convert_wav(wav, nchannels, 60*self.fs)
            
            
        else:
            wav.setpos(0)
            sound = self.convert_wav(wav, nchannels, self.length)
            
        avg = numpy.mean(abs(sound))
        del(sound)
        wav.setpos(0)
        avg = round(avg, 4)
        return avg
            
            
    def everyOther (self,v, offset=0):
        return [v[i] for i in range(offset, len(v), 2)]
        
    
    def read_Wav(self, restart = False):
        '''
        The main module the runs through the entire recording. Makes call to
        convert_wav, return_db, and Sound_Analyze_V#. 
        
        '''
        
        if restart == False:
            wav = wave.open (self.wav_file, "r")
            (nchannels, sampwidth, self.fs, self.length, comptype, compname) = wav.getparams ()
            chunk = int(self.Blocksize*self.fs) #CHUNK MUST BE SMALLER THAN WHOLE FILE, will be taken from input file soon
            self.end_index = chunk
            remainder = (self.length) % chunk
            times = int((self.length)/chunk)
            self.avg = self.get_average(wav, nchannels)
        else:
            wav = wave.open(self.wav_file, "r")
            chunk = int(self.Blocksize*self.fs)
            nchannels = wav.getnchannels()
            sound_left = self.length - self.start_index
            times = int((sound_left)/chunk)
            remainder = sound_left % chunk
            wav.setpos(self.start_index)
        if times > 0:   
            for i in range(times -1):
                sound = self.convert_wav(wav, nchannels, chunk)
                db = self.return_db(sound)
                
                self.start_index = self.end_index
                self.end_index = self.end_index + chunk
                wav.setpos(self.start_index)
                
                self.restart_write()
                Sound_Analyze_V4.main(sound, self.raw, self.start_index, self.end_index, self.fs, self.percentile, self.lhertz, self.uhertz, self.step, self.threshold, self.mingap, self.fft_Q, self.time_Q, self.filt_Q, self.output, db)
               
            sound = self.convert_wav(wav, nchannels, chunk + remainder)                  
            db = self.return_db(sound)
             
        else:
            sound = self.convert_wav(wav, nchannels, remainder)
            db = self.return_db(sound)
            
        self.restart_write()
        Sound_Analyze_V4.main(sound, self.raw, self.start_index, self.end_index, self.fs, self.percentile, self.lhertz, self.uhertz, self.step, self.threshold, self.mingap, self.fft_Q, self.time_Q, self.filt_Q, self.output, db)
        
        comp_time = time.clock() - self.time_1
        self.comp_time = self.reformatTime(comp_time)
        self.time_output()
    
    def convert_wav(self, wav, nchannels, sound):
        '''
        Converts the standard wav encoding to integer form.
        "%dh" dictates our format, while (chunk)*nchannels is the size
        of the array we are analyzing.
        '''
        new_frames = wav.readframes(sound)
        sound_chunk = struct.unpack_from("%dh" % (sound)*nchannels, new_frames)
        sound_chunk = list(sound_chunk)
            
            
        if nchannels == 2:
            left = numpy.array(self.everyOther(sound_chunk, 0))
            right = numpy.array(self.everyOther(sound_chunk, 1))
            sound = (left + right)/2
        else:
            sound = numpy.array(sound_chunk)
        return sound
        
    def return_db(self, chunk):
        '''
        Converts raw amplitude of sound files to decibels. Decibels are a
        logrithmic transform of the quotient of the amplitude
        of a specific time interval over the amplitude of silence. This means
        any silence will have an amplitude of 0. This helps distinguish between
        noise and not noise. The 'silence value' is calculated by taking the
        average amplitude of a random minute of sound in the file."
        '''
        zeros = numpy.nonzero(chunk == 0)
        
        for i in zeros[0]:
            chunk[i] = 0.01
        
        chunk = abs(chunk)
        db = 10*numpy.log(chunk/self.avg)
        
        return db
    
    def reformatTime(self, seconds):
        '''
        Reformats time to the h:m:s format for time stamps.
        '''
        decimal = seconds%1
        seconds = int(seconds)
        hours = seconds/3600
        minutes = (seconds - hours*3600)/60
        seconds = (seconds - (hours*3600 + minutes*60))
        return str(hours)+'h:' +str(minutes)+'m:'+str(seconds+decimal)+ 's'
        
    def format_output(self):
        '''
        Module that formats output so there is a ten second break between all
        recorded time stamps.
        '''
        f = open(self.output, 'r')
#        if 'VID' in self.raw:
#            splitter = self.raw.split(' ')
#            f_out = splitter[1] + '_' + splitter[3] + '_FormOut.txt'
#            out = open(f_out, 'w')
#        else:
#            out = open(self.raw + '_FormOut.txt', 'w')
        out = open(self.raw + '_FormOut.txt', 'w')
        sound_number = 0
        first = 0
        last = 0 
        line = f.readline()
        sline = line.split()
        n = len(sline)
        while n > 0:
            if first == 0 or (int(sline[0]) - last) >= int(self.mingap*self.fs):
                out.write("SOUND " + str(sound_number) + '\t'+ self.reformatTime(int(sline[0])*1.0/self.fs) + "\n")
                sound_number = sound_number + 1
                first = 1
                last = int(sline[0])
            line = f.readline()
            sline = line.split()
            n = len(sline)
        
        f.close()
        out.close()
#        if 'VID' in self.raw:
#            cwd = os.getcwd()
#            outdir = os.path.join(cwd, f_out)
#            vid_dir, ext = os.path.split(self.wav_file)
#            shutil.copy(outdir, vid_dir)
        
            
        
    def delete_file(self):
        '''
        Module to delete self.restart_file and self.num_file.
        Only executed after the program has run to completion.
        '''
        
        os.remove(self.restart_file)
        os.remove(self.output)
        os.remove(self.wav_file)
        
        
    def run_restart(self):
        '''
        A module that is run if the global variable 'restart' is True. Should only be run if 
        Analysis of the .wav file of interest originally crashed. Whether or not a restart
        should be run will be inputted into the input file.
        '''
        self.read_restart()
        self.read_Wav(True)
        
    def time_output(self):
        time_length = self.length * 1.0/self.fs
        time_length = self.reformatTime(time_length)
        out = open('Time_out_before.txt', 'a')
        out.write(str(self.raw + '\t' + str(self.comp_time) + '\t' + str(time_length) + '\t' + str(self.Blocksize) + '\n'))
        out.close()
        
    def read_restart(self):
        '''
        A module to read information from the restart file. Called after
        originally calculating Maxratio as well as durin a program restart.
        '''
        filename = open(self.restart_file, 'r')
        restart_list = []
        for i in range(6):
            line = filename.readline()
            line_split = line.split()
            restart_list.append(line_split[0])
        self.start_index = int(restart_list[1])
        self.end_index = int(restart_list[2])
        self.fs = int(restart_list[3])
        self.length = int(restart_list[4])
        self.avg = float(restart_list[5])
        filename.close()
        
            
    def restart_write(self):
        '''
        Write necessary variables to a restart file. The restart file will be
        used to continue analysis should the program crash during the initial 
        run.
        '''
        filename = open(self.restart_file, 'w')
        filename.write(self.output + "\n")
        filename.write(str(self.start_index) + "\n")
        filename.write(str(self.end_index) + "\n")
        filename.write(str(self.fs) + "\n")
        filename.write(str(self.length) + "\n")
        filename.write(str(self.avg) + "\n")

        
        filename.close()

def run(f):
    b = Restart(f)
