# Read - file 
from YVideo import YUVReader
import sys
Ysize = [352,288]
Ystart = 0
Yend = 150
Yfps = 1
Yreader = YUVReader("akiyo_cif.y", Ysize, Ystart, Yend, Yfps, "out/",False)
sys.stdout.write("Conversion completed!")
sys.exit() 