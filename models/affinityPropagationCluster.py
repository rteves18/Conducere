#!/usr/bin/python

# CSE 481I - Sound Capstone wi16
# Conducere (TM)

# Clustering

import sys

import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
import math
from util import clean

# The number of clusters should be this * number of y values

# Gives the usage of this program
def usage():
  print "Usage: python run.py kMeansCluster [iterations] [data_file] [features to use...]"

# Executes a model for clustering data. Treats the first feature as the dependent
# feature.
#
# For arguments, takes the data file, and an optional list of features to use. If
# no list is given, will use all features. Outputs a map of each cluster, in the
# form of majority playlist and the percentage of the cluster belonging to that
# playlist.
def execute(args):
  np.random.seed(42)
  if len(args) < 1:
    usage()
    sys.exit()
  names, y, x = parse(args[0])
  indices = [int(i) for i in args[1:]]
  relevant_names = names[1:]
  x = clean(relevant_names, x)
  if len(indices) > 0:
    x = np.asarray([[sample[i] for i in indices] for sample in x])
    relevant_names = [relevant_names[i] for i in indices]
  print "Clustering on", str(relevant_names) + "..."

  labels = np.unique(y)
  af = AffinityPropagation(damping=0.52)
  x_train = random_selection(x, int(len(x) * 0.6))
  af.fit(x_train)
  y_pred = af.predict(x)
  un = np.unique(y_pred)

  counts = get_cluster_counts(y, y_pred)
  totals = {}
  print counts
  for i, mapping in counts.iteritems():
    s = sum(mapping.values())
    if s != 0:
      totals[i] = sum(mapping.values())
  finals = get_final_mapping(counts, totals)
  if len(finals) < len(labels):
    print "WARNING: Not all labels accounted for!"
  print "FINAL CLUSTERS", finals
  print "NUM CLUSTERS", len(counts)
  print "NUM Y_PRED", len([y for y in y_pred if type(y) is not np.ndarray])
  print
  print "ACCURACY", accuracy(finals, labels)
  return accuracy(finals, labels), len(counts)


# Parses the given file into a matrix of data. The depenedent variable is assumed
# to be at the beginning
def parse(filename):
  raw = [[feature for feature in line.strip().split(',')] for line in open(filename, 'r')]
  names = raw[0]
  raw = raw[1:]
  np.random.shuffle(raw)
  dependent = [sample[0] for sample in raw]
  independent = [sample[1:] for sample in raw]
  independent = [[float(sample_point) for sample_point in sample] for sample in independent]
  return names, dependent, np.asarray(independent)

# Given the actual y-values 'y' and the predicted values 'y_pred', returns the counts
# for each playlist in each cluster.
#
# Returns a map, containing an id for each cluster. Each id maps to another map,
# containing playlist labels as keys. Each label maps to the count of that label
# in the cluster.
def get_cluster_counts(y, y_pred):
  unique = np.unique(y_pred)
  labels = np.unique(y)
  counts = {un : {label : 0 for label in labels} for un in unique}
  for i in range(len(y)):
    if type(y_pred[i]) is not np.ndarray:
      counts[y_pred[i]][y[i]] += 1
  return counts

# Returns the final mapping, which is a decided playlist and a percentage of that cluster
# made up of that playlist
def get_final_mapping(counts, totals):
  clusters = [(max(mapping, key = lambda k : mapping[k]), mapping) for key, mapping in counts.iteritems()]
  combined = {}
  for cluster in clusters:
    old = combined.get(cluster[0], {})
    new = {}
    for key in cluster[1]:
      new[key] = cluster[1][key] + old.get(key, 0)
    combined[cluster[0]] = new
  return combined

def probability(final):
  return {name : value[name] / float(sum([v for k, v in value.iteritems()])) for name, value in final.iteritems()}

def accuracy(final, labels):
  # tuple for (right, wrong)
  accuracy = {label : [0, 0] for label in labels}
  for name, data in final.iteritems():
    for dataName, dataValue in data.iteritems():
      if name == dataName:
        accuracy[dataName][0] += dataValue
      else:
        accuracy[dataName][1] += dataValue
  final_accuracy = {name : (value[0] / float(sum(value))) if sum(value) != 0 else 0 for name, value in accuracy.iteritems()}
  return final_accuracy

# Returns an array of size num_samples, that is a random selection from x
# without replacement
def random_selection(x, num_samples):
  selector = [i for i in range(len(x))]
  selection = np.random.choice(a=selector, size=len(x / 2), replace=False)
  return[x[i] for i in selection]
