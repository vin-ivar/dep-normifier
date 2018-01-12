from argparse import ArgumentParser
from nltk import FreqDist
import sys

class Recommender:
	# direction ltr assumes treebank 1 is accurate and 2 needs fixing
	def __init__(self, normaliser, conllu, direction='ltr', cutoff=0.9, maximise_information=True):
		check_context = FreqDist(normaliser.print_full())
		size = int(len(check_context) * cutoff)
		check_context = [i[0] for i in check_context.most_common(size)]
		if direction == 'ltr':
			self.check_context = {i.split(':')[1]: i.split(':')[0] for i in check_context}
		else:
			self.check_context = {i.split(':')[0]: i.split(':')[1] for i in check_context}

		self.check_free = set(normaliser.print_stream())
		self.conllu = conllu
		self.maximise_information = maximise_information

	def recommend_with_context(self):
		full = []
		blokk, kummenti = [], []
		for line in self.conllu:
			if line == '\n':
				blokk.append(line)
				full.extend(kummenti)
				full.extend(blokk)
				kummenti, blokk = [], []
			elif line[0] == '#':
				kummenti.append(line)
			else:
				cols = line.split("\t")
				num, feats = cols[0], cols[5]
				if feats in self.check_context:
					string = ""
					if self.maximise_information:
						f1, f2 = feats.split('|'), self.check_context[feats].split('|')
						f1 = {k: v for k, v in [i.split("=") for i in f1]}
						f2 = {k: v for k, v in [i.split("=") for i in f2]}

						for k in f2:
							if f2[k] == '_':
								f2[k] = f1[k]
						
						for k in f2:
							string += "{}={}".format(k, f2[k])
							
						# string = string[:-1]
					else:
						string = self.check_context[feats]

					string = "# REPLACE {} with {}\n".format(num, string)
					kummenti.append(string)

				blokk.append(line)

		return full

class Normaliser:
	# f1, f2: PARSED treebanks in CoNLL-U
	# align: alignment from language 1 to 2
	def __init__(self, f1, f2, align):
		self.out = []
		with open(f1) as f1, open(f2) as f2, open(align) as align:
			self.f1 = self.reconstruct(f1.read().split("\n"))
			self.f2 = self.reconstruct(f2.read().split("\n"))
			self.align = align.read().split("\n")[:1000]

		for n, (a, b, l) in enumerate(zip(self.f1, self.f2, self.align)):
			if l == "":
				continue
			rels = l.split(" ")
			m = map(lambda x: (int(x.split("-")[0]), int(x.split("-")[1])), rels)
			for pair in m:
				self.out.append((a[pair[0]], b[pair[1]]))


	def reconstruct(self, blokk):
		out, curr = [], []
		for line in blokk:
			if line == '':
				out.append(curr)
				curr = []
			elif line[0] == '#':
				continue
			else:
				cols = line.split("\t")
				# 1 -> form, 5 -> feats
				curr.append((cols[1], cols[5]))

		return out


	def from_dict(self, f1, f2, unmatched):
		out = []
		keys = set(f1.keys()).union(f2.keys())
		for key in keys:
			try:
				if not unmatched:
					string = "{}:{}:{}".format(key, f1[key], f2[key])
				else:
					if f1[key] == f2[key]:
						continue
					else:
						string = "{}:{}:{}".format(key, f1[key], f2[key])
			except:
				if key not in f1.keys():
					string = "{}:{}:{}".format(key, '_', f2[key])
				else:
					string = "{}:{}:{}".format(key, f1[key], '_')
			out.append(string)
		return out

	def from_dict_with_context(self, f1, f2):
		out = []
		lhs, rhs = "", ""
		keys = set(f1.keys()).union(f2.keys())
		for key in keys:
			try:
				# hacky: just ignore char 1 to avoid the line
				lhs += "|{}={}".format(key, f1[key])
			except:
				lhs += "|{}=_".format(key)
			
			try:
				rhs += "|{}={}".format(key, f2[key])
			except:
				rhs += "|{}=_".format(key)
			
			if lhs != rhs:
				out.append("{}:{}".format(lhs[1:],rhs[1:]))
		return out


	def pair_feats(self, pairs, unmatched=False, context=False):
		out = []
		for l1, l2 in pairs:
			w1, w2, f1, f2 = l1[0], l2[0], l1[1], l2[1]
			# dicts are easier to query
			if f1 == '_':
				f1 = {}
			else:
				f1 = {k: v for k, v in [eqn.split("=") for eqn in f1.split("|")]}
			if f2 == '_':
				f2 = {}
			else:
				f2 = {k: v for k, v in [eqn.split("=") for eqn in f2.split("|")]}

			if context:
				out.extend(self.from_dict_with_context(f1, f2))
			else:
				out.extend(self.from_dict(f1, f2, unmatched))

		return out


	def print_stream(self):
		return self.pair_feats(self.out, True)

	def print_full(self):
		return self.pair_feats(self.out, context=True)
