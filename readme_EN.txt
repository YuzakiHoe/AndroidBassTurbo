This program is based on the HapticAdd program and uses a low-pass filter to make the linear motor play low-frequency signals as much as possible to enhance the bass effect
At present, it is still in the experimental stage, and the low-frequency signal filtered by BassTurboPure is purer than that filtered by BassTurbo
 Required dependencies to be installed
   pip install pydub numpy scipy matplotlib mutagen
How to use
  Enhance low frequencies below 250Hz (default setting)
    python bassTurbo.py music.ogg
  Enhance low frequencies below 120Hz (suitable for heavy bass)
    python bassTurbo.py beat.ogg -c 120
  Enhance visual effects
    python bassTurbo.py drum.ogg -p -b 3.0
**************notice**************
  You must first convert the audio to 48kHz
  Then convert it to. ogg format file!!!
**********************************
Note: Enter after the command character
-O Output file name can be specified
Default to automatic generation
-B can set the enhancement factor
Default is 2.0
-T can set the sensitivity of vibration triggering
Default is 0.15
Generate pure low-frequency vibration
python bassTurboPure.py music.ogg
The specific effect depends on the equipment

By  YuzakiPTeam@2025
This is the first time there is a problem with this program. Please provide feedback and understanding
Thank you all for your support
Not currently supported for Xiaomi devices (missing relevant APIs)
Currently, the OnePlus 13 model that has passed testing and achieved good results
Two audio files are included in the project, where AF is the sample audio with metadata loaded and BF is the sample audio without metadata loaded
I am not responsible for any problems caused by self testing of other models