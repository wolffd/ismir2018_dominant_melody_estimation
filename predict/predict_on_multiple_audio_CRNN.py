#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
import threading
import multiprocessing # https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread

from predict_on_single_audio_CRNN import *

process_timeout = 10 # seconds

# RunCmd(["./someProg", "arg1"], 60).Run()
#class RunCmd(threading.Thread):
#    def __init__(self, cmd, timeout):
#        threading.Thread.__init__(self)
#        self.cmd = cmd
#        self.timeout = timeout

#    def run(self):
#        self.p = subprocess.Popen(self.cmd)
#        self.p.wait()

#    def Run(self):
#        self.start()
#        self.join(self.timeout)

#        if self.is_alive():
#            self.p.terminate()      #use self.p.kill() if process needs a kill -9
#            self.join()


if __name__ == '__main__':
    # a dataset name can be input as the first argument, e.g. "python predict_on_single_audio mysupercooldataset"
    # this assumes that there is a folder "mysupercooldataset_audio" in ../../ from this file
    
    if len(sys.argv) >= 2:
        dataset = sys.argv[1]
        rootDir = get_path_to_dataset_audio(dataset)
        for dirName, subdirList, fileList in os.walk(rootDir):
            # print('Found directory: %s' % (dirName))
            
            abbr_index = dirName.find(dataset + "_audio") + len(dataset + "_audio") + 1
            if (abbr_index < len(dirName)):
                abbreviated_dirname = dirName[abbr_index:]
            else:
                abbreviated_dirname = ''
            # print('Processing: %s' % (abbreviated_dirname))
             
            # make all the new safe paths
            if not os.path.exists(get_model_output_save_path(dataset) + '/' + abbreviated_dirname):
                os.makedirs(get_model_output_save_path(dataset) + '/' + abbreviated_dirname)
                
            if not os.path.exists(get_hf0_path(dataset) + '/' + abbreviated_dirname):
                os.makedirs(get_hf0_path(dataset) + '/' + abbreviated_dirname)                
            
            for fname in fileList:
                if not ('.aiff') in fname.lower():
                    continue
                try:
                    # print('\t%s' % fname)
                    full_track_name = abbreviated_dirname + '/' + fname
                    track_name = full_track_name[:-4]
                    # track_name = 'test'
                    
                    # convert to wav if transformed
                    transformed = False
                    if not fname.lower().endswith('.wav'):
                        conversion.convert_to_wav(rootDir + "/" + full_track_name)
                        transformed = True
                    
                    HF0_fpath = '{0}/{1}.h5'.format(get_hf0_path(dataset),track_name)
                    audio_fpath = '{0}/{1}.wav'.format(get_path_to_dataset_audio(dataset),track_name)
                    print("Processing: %s" % audio_fpath)
                    
                    
                    # threading to stop if runs longer than timeout
                    if process_timeout > 0:
                        thread = multiprocessing.Process(target = main_prediction, args = (audio_fpath, dataset, False))
                        thread.start()
                        thread.join(process_timeout)
                        
                        if thread.is_alive():
                            print('Warning: terminating process due to exceeded timeout of %d seconds: %s' % (process_timeout, audio_fpath))
                            thread.terminate()      #use self.p.kill() if process needs a kill -9
                            thread.join()
                    else:
                        main_prediction(file_path=audio_fpath, dataset_name = dataset, evaluate_results=False)
                    
                    if transformed and not fname.lower().endswith('.wav'):
                        os.remove(rootDir + "/" + full_track_name[:-4] + '.wav')
                        
                except Exception as e: 
                    print ('Warning: could not process file %s: %s' % (full_track_name,str(e)))