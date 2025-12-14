import sys
import argparse
from answerFinal import identifyUpstreamOriginNodes, AdjacencyMapMutant
"""
Usage specify a file to test against

python fileLoader.py -f 001.txt
"""
"""
  Usage
  python file_tester.py -f a.txt
"""


def runFile(fileName: str):
    try:
        with open("testCases/" + fileName, 'r', encoding='utf-8') as inputfile:
            lines = inputfile.readlines(-1)
            pairs = int(lines[0].strip())
            amm = AdjacencyMapMutant(True)
            for i in range(1, pairs + 1):
                pair = lines[i].strip().split("→")
                print(f"pair is {pair}")
                amm.addEdge(pair[0], pair[1])
            return identifyUpstreamOriginNodes(amm)
    except FileNotFoundError:
        print("The file was not found.")
    except IOError as e:
        print(f"An I/O error occurred: {e}")



if __name__ == '__main__':
    #print(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='file', type=str, help='File input')
    args = parser.parse_args()

    #print("The file is " + str(args.file))

    result = runFile(args.file)
    print(f"Your result is: {result}")
