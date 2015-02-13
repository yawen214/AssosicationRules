""" 
assoication.py by Yawen Chen & Brian Charous 
for CS324 Winter 2015
PART 2 of Association Rule Assignment (Part2)
To run:
arguments: -s support_threhold -c confidence_threshold -f movie_names_data -d dataset
for example: pypy association.py -f movies.dat -d ratings.dat -s 1500 -c 80

"""
from __future__ import division
import sys
import argparse
import time
import itertools

def get_items(filename):
    """ read in data from both the item file.
         return a dictionary of items with ID and movie name
         return an items_set (set) with movie IDs in it
    """
    items_dict = dict() # a dictionary with ID and the movie name
    all_items_set = set()
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split("::")
            components = [c for c in parts]
            items_dict[int(components[0])] = components[1]
            all_items_set.add(components[0])
    return items_dict, all_items_set

def get_transactions(filename):
    ''' return tansactions lists consists of a transactions set
        to avoid storing all transactions in memory, we don't use this function
        for part II.
    '''
    transactions_list = []
    transaction = set()
    with open(filename, 'r') as f:
        cur_id = 1
        for line in f:
            parts = line.split("::")
            components = [c for c in parts]          
            if  cur_id != int(components [0]):
                transactions_list.append(transaction)
                transaction = set()
                cur_id = int(components[0])
            transaction.add(int(components[1]))
    return transactions_list

def freq_item_generate(threshold, items_sets, transactions_list):
    ''' Return itemset of size one with support larger or equal to the threshold.
        Current version only return k =1 size freq items
    '''
    freq_itemsets = []
    for item in items_sets:   
        count = 0
        for transaction in transactions_list:        
            if int(item) in transaction: #version 0: only care about k =1
                count += 1
        if count >= threshold:
            freq_itemsets.append(set([int(item)]))
    return freq_itemsets

def gen_candidates(itemsets):
    """ takes a list of itemsets and a size k and
    uses the F_{k-1}xF_{k-1} technique for candidate generation """

    # sort itemsets, pull out last item (i.e. get first k-2 items), 
    # ke track of last item
    km2 = []
    for s in itemsets:
        s_sort = sorted(s)
        km2.append((set(s_sort[:-1]), set([s_sort[len(s_sort)-1]])))

    candidates = []
    for pair in itertools.combinations(km2, 2):
        s1 = pair[0][0]
        s2 = pair[1][0]
        if s1 == s2:
            last_elem1 = pair[0][1]
            last_elem2 = pair[1][1]
            if last_elem1 != last_elem2:
                # append the union of elements 0 - k-2, elements @ k-1 from both lists
                candidates.append(s1 | last_elem1 | last_elem2)
    return candidates

def create_hash_tree(candidates):
    """ build a hash tree from candidates """
    tree = {}
    for candidate in candidates:
        tree = append_candidate_to_tree(sorted(list(candidate)), tree)
    return tree

def append_candidate_to_tree(candidate, tree):
    """ append a candidate (SORTED LIST) to the hash tree """
    val  = candidate[0]
    if len(candidate) == 1:
        tree[val] = 0
        return tree
    else:
        if val in tree:
            append_candidate_to_tree(candidate[1:], tree[val])
            return tree
        else:
            tree[val] = append_candidate_to_tree(candidate[1:], {})
            return tree

def increment_support_count(transaction, candidates, hash_tree):
    """ increment the count of each itemset of size k in a given transaction """
    for candidate in candidates:
        candidate_in_transaction = True
        for item in candidate:
            if item not in transaction:
                candidate_in_transaction = False
                break
        if candidate_in_transaction:
            __increment_support_count(sorted(list(candidate)), hash_tree)

def __increment_support_count(itemset, hash_tree):
    """ traverse the hash tree and actually increment the count for an itemset """
    item = itemset[0]
    if len(itemset) == 1:
        if item in hash_tree:
            assert type(hash_tree[item]) is int
            hash_tree[item] = hash_tree[item] + 1
    else:
        if item in hash_tree:
            __increment_support_count(itemset[1:], hash_tree[item])

def count_support(filename, hash_tree, candidates):
    """ read transactions from file, increment hash tree leaves if subset of transaction 
    is a candidate """
    transaction = set()
    with open(filename, 'r') as f:
        cur_id =1
        for line in f:
            parts = line.split("::")
            components = [c for c in parts]
            if cur_id != int(components[0]):
                increment_support_count(transaction, candidates, hash_tree)
                transaction = set()  #reset transaction
                cur_id = int(components[0]) #set cur id
            transaction.add(int(components[1])) #add movie id to the current transaction
            
def prune_candidates(hash_tree, candidates, threshold):
    """ return a list of itemsets that appeared more than the threshold number of times
    in the dataset """
    pruned = []
    for c in candidates:
        support  = is_candidate_supported(hash_tree, c, threshold)
        if support >= threshold:
            pruned.append((c, support))
    return pruned

def is_candidate_supported(hash_tree, candidate, threshold):
    """ traverse hash tree and return the support threshold for a candidate """
    lc = list(candidate)
    item = lc[0]
    if len(candidate) == 1:
        if item in hash_tree:
            assert type(hash_tree[item]) is int
            if hash_tree[item]>threshold:
                #rule_generation(item,hashtree)
                return hash_tree[item]
    else:
        if item in hash_tree:
            return is_candidate_supported(hash_tree[item], lc[1:], threshold)
    return 0

def apriori(transactions_filename, threshold):
    """ run apriori algorithm to find frequent itemsets """
    # get all item ids, say these are the "candidates" of size 1
    all_pruned = []
    k = 1
    candidates = set()
    with open(transactions_filename, 'r') as f:
        for line in f:
            parts = line.split("::")
            candidates.add((int(parts[1]),))
    candidates = [set(c) for c in candidates]
    tree = create_hash_tree(candidates)
    count_support(transactions_filename, tree, candidates)
    pruned = prune_candidates(tree, candidates, threshold)
    # pruned_sets = [p[0] for p in pruned]
    all_pruned.extend(pruned)
    print "{0} candidates, {1} items for k={2}".format(len(candidates), len(pruned), k)
    k = 2
    # apriori
    while True:
        candidates = gen_candidates([p[0] for p in pruned])
        tree = create_hash_tree(candidates)
        count_support(transactions_filename, tree, candidates)
        pruned = prune_candidates(tree, candidates, threshold)
        # pruned_sets = [p[0] for p in pruned]
        all_pruned.extend(pruned)
        print "{0} candidates, {1} items for k={2}".format(len(candidates), len(pruned), k)
        if len(pruned) == 0:
            return all_pruned
        k+=1
    return all_pruned

def generate_rules(freq_itemsets, confidence_threshold):
    """ generate rules based on frequent itemsets and a confidence threshold """
    supports = {}
    # change (set([A,B,C,...,]), supprt) into dict
    for s in freq_itemsets:
        supports[tuple(s[0])] = s[1]

    rules = []
    for s in freq_itemsets:
        items = s[0]
        support = s[1]
        if len(items) > 1:
            for combo in itertools.combinations(items, len(items)-1):
                lhs = set(combo)
                rhs = lhs ^ items
                numerator = 0
                denominator = 0
                union = tuple(lhs | rhs)
                if union in supports:
                    numerator = supports[union]
                if tuple(lhs) in supports:
                    denominator = supports[tuple(lhs)]
                # confidence = support(I U {j})/support(I)
                if numerator/denominator*100 > confidence_threshold:
                    rules.append((lhs, list(rhs)[0]))
    return rules


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--support_threshold', type= int, required=True, help='Input wanted support threshold')
    parser.add_argument('-c', '--confidence_threshold', type= int, required = True, help = 'Input confidence threshold')
    parser.add_argument('-f', '--items_file', required=True, help='The file name of the itemset')
    parser.add_argument('-d', '--dataset_file', required=True, help='The file name of the dataset')

    args = parser.parse_args()
    support_threshold = int(args.support_threshold)
    # read in movie names
    items_dict, all_items_set = get_items(args.items_file) 
    print "=================================================="
    print " Finding frequent itemsets with Apriori Algorithm "
    print "=================================================="
    freq_itemsets = apriori(args.dataset_file, support_threshold)
    rules = generate_rules(freq_itemsets, int(args.confidence_threshold))
    print "=================================================="
    print " Rules generated with confidence greater than {0} ".format(args.confidence_threshold)
    print "=================================================="
    for rule in rules:
        lhs = rule[0]
        rhs = rule[1]
        lhs_movies = '{'
        for movie in lhs:
            # get the name of every movie
            lhs_movies += str(items_dict[movie]) + ', '
        lhs_movies = lhs_movies[:len(lhs_movies)-2] + "}"
        print "{0} -> {1}".format(str(lhs_movies), '{' + items_dict[rhs] + '}')

if __name__ == '__main__':
    main()