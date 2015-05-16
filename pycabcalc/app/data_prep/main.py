import sys

import manhattan
import shortestDist
import weather

def run(month, typ):
    
    if typ=='manhattan':
        manhattan.mark(month)

    elif typ=='shortestDist':
        shortestDist.mark(month)

    elif typ=='weather':
        weather.mark(month)



if __name__ == "__main__":

    month = int(sys.argv[1])
    typ = sys.argv[2]

    run(month, typ)

