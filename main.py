from argparse import ArgumentParser
from dep import Normaliser, Recommender
import sys

parser = ArgumentParser()
parser.add_argument("--t1", help="treebank 1")
parser.add_argument("--t2", help="treebank 2")
parser.add_argument("--align", help="alignment")
args = parser.parse_args()
t1, t2, align = args.t1, args.t2, args.align

conllu = []
for line in sys.stdin:
	conllu.append(line)

n = Normaliser(t1, t2, align)
r = Recommender(n, conllu)
# for line in n.print_full():
	# print(line)
for line in r.recommend_with_context():
	sys.stdout.write(line)
