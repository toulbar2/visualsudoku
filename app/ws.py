""" read_and_solve method calling ws request """
  
__author__    = "Nathalie Rousse"
__copyright__ = "Copyright 2020, INRAE"
__license__   = "MIT"

import requests

def read_and_solve(image, output, keep=None, border=None, time=None) :
    """Sends POST request and return solution image file

    Memo : some parameters of url_vsudoku request :
           - todownload="no"
           - returned_type ="stdout" or "stdout.txt" or "run.zip"

    """

    url_vsudoku = 'http://147.100.179.250/api/tool/vsudoku'

    files = {'file': open(image, 'rb')}

    data = {'returned_type':'stdout'}
    if keep is not None :
        data['keep'] = keep
    if border is not None :
        data['border'] = border
    if time is not None :
        data['time'] = time

    r = requests.post(url_vsudoku, data=data, files=files)
    
    with open(output, 'wb') as solution_file:
        solution_file.write(r.content)

#memo
#python3 toulbar2_visual_sudoku_puzzle.py -m digit_classifier.h5 -i sudoku_poster.jpg -o WSsolution_poster.jpg -k 70
#echo "[INFO] toulbar2_visual_sudoku_puzzle.py running with options : -i $1 -o solution.jpg -k $2 -b $3 -t $4"
#-i $1 -k $2 -b $3 -t $4

