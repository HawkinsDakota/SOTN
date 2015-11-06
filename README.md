# SOTN
Code for detecting singing on the nest in field recordings.

Code is messy and poorly structure, but it works. Current work is focused on cleaning up the code and supporting multi-core processing.

Video files are analyzed by running either of two .sh files:
$bash vidcon_avi.sh
or
$bash vidcon_wmv.sh

Right now, only .avi and .wmv files are supported, but that can easily be expanded by editing the existing .sh files or creating new .sh files that support different extensions. In theory, any vieo file supported by ffmpeg should work.

Outline for detecting singing on the nest:

  Automated analysis starts by ripping the audio track from corresponding video files. The program selects a random one-minute sound interval and calculates the average amplitude. This amplitude value acts as an estimation of the average loudness of background sound and is used in decibel filtration. Analysis continues at the beginning of the sound file and breaks the file into one-minute sections. Partitioning the file is necessary to prevent computer crashes and improve efficiency. Once the first one-minute sound interval is selected, the sound was run through a frequency filter.
  Frequency filtration of one-minute sections consists of transforming sound into the frequency domain using the Fast Fourier Transform. Any samples with frequencies outside of the 2 kHz – 7kHz range are forced to zero amplitude to filter out non-bird sounds. The 2 kHz – 7kHz range includes the characteristic frequency range of avian species (Nemeth et al. 2012) and most effectively isolates songs in test samples. The lower bounds in frequency filtering excluded most anthropogenic noise and upper bounds excluded most random noise (Nemeth et al. 2012). While frequency filtration excludes most non-bird sounds, it has no way to determine whether singing was occurring on the nest or in the background. To better isolate SOTN, the sound interval is run through an additional decibel filter after frequency filtration.
  Because video recorders were placed on the nest, it was assumed if SOTN occurred, the close proximity to the camera would result in large decibel values. Therefore, filtering the sound for large amplitude values results in better isolation of SOTN intervals. To begin decibel filtration, sound is transformed back into the time domain using the Inverse Fast Fourier Transform. Decibels are calculated by using the calculated average loudness and the amplitude of a given sample where dB= 10log((Sample Amplitude)/(Average Loudness )). Samples are then filtered to determine whether their decibel value is in the 90th percentile and if the value is greater than zero.  If the sample did not meet both standards, the amplitude of the sample was forced to zero. 
  Keeping only values in the 90th percentile produced the best song isolation in test files; removing all samples with dB ≤ 0 meant we were not selecting any samples with comparable amplitudes to the average loudness, helping exclude background noise. At this point, the sound interval contains only sound that fit acoustic characteristics of SOTN; however, the program did not have a reliable mechanism to determine at what time singing was occurring.  
  The program compares the one-minute section beofre and after filtrationto determine when SOTN occurred. Comparison involved determining the percent change of amplitude before and after filtration over a series of 15s time intervals. Percent change was calculated using percent change=((avg.amp.before-avg.amp.after))/(avg.amp.before). Because we removed sound samples when characteristic conditions for SOTN were not met, having a low percent change associated with characteristic features of SOTN. If the percent change was less than 10%, the starting timestamp is recorded and exported to a temporary file. The process is then repeated for the entire audio file.
  After all of the sound has been analyzed, the program combs through time stamps in the temp file. If time stamps are +/- 10 seconds from each other, redundant values are removed and only a single time stamp is left. After all redundant time stamps are removed, and .txt file is outputted containing time stamps for manual inspection.

work cited:

Nemeth, E. Pieretti, N. Zollinger, SA., Geberzahn, N., Partecke, J. Miranda, AC., Brumm, H. (2013). Bird song and anthropenic     noise: vocal constraints may explain why birds sing higher-frequency songs in cities. Proc R Soc B. 280: 20122798.   http://dx.doi.org/10.1098/rspb.2012.2798
