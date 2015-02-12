""" 
assoication.py by Yawen Chen & Brian Charous 
for CS324 Winter 2015
PART 2 of Association Rule Assignment (Part2)
To run:
python -s --threshold -f itemsets -d datasets
for example: python association.py -s 1000 -c 20 -f movies.dat -d ratings.dat

"""

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
    return [c for c in candidates if is_candidate_supported(hash_tree, c, threshold)]

def is_candidate_supported(hash_tree, candidate, threshold):
    lc = list(candidate)
    item = lc[0]
    if len(candidate) == 1:
        if item in hash_tree:
            assert type(hash_tree[item]) is int
            if hash_tree[item]>threshold:
                #rule_generation(item,hashtree)
            return hash_tree[item] > threshold
    else:
        if item in hash_tree:
            return is_candidate_supported(hash_tree[item], lc[1:], threshold)
    return False

def apriori(transactions_filename, threshold, max_k):

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
    all_pruned.extend(pruned)
    print "{0} candidates, {1} items for k={2}".format(len(candidates), len(pruned), k)
    k = 2
    # apriori
    while k <= max_k:
        candidates = gen_candidates(pruned)
        tree = create_hash_tree(candidates)
        count_support(transactions_filename, tree, candidates)
        pruned = prune_candidates(tree, candidates, threshold)
        all_pruned.extend(pruned)
        print "{0} candidates, {1} items for k={2}".format(len(candidates), len(pruned), k)
        if len(pruned) == 0:
            return all_pruned
        k+=1
    return all_pruned

#
def rule_generation():
    return 1
#

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--support_threshold', type= int, required=True, help='Input wanted support threshold')
    parser.add_argument('-c', '--confidence_threshold', type= int, required = True, help = 'Input confidence threshold')
    parser.add_argument('-f', '--items_file', required=True, help='The file name of the itemset')
    parser.add_argument('-d', '--dataset_file', required=True, help='The file name of the dataset')

    args = parser.parse_args()
    # Set up itemsets and datasets 
    sys.stdout.write("Working on seting up itemsets... ")
    sys.stdout.flush()
    threshold = int(args.support_threshold)
    support_threshold = int(args.support_threshold)
    items_dict, all_items_set = get_items(args.items_file)  # read in all itemsets
    print "done!"
    print "==========================="
    k = len(all_items_set)
    start = time.time()
    freq_itemsets =apriori(args.dataset_file, support_threshold, k)
    end = time.time()
    sys.stdout.write(" done in {0}s\n\nFound:\n".format(end-start))
    i = 0
    for set in freq_itemsets:
        movies = []
        i+= 1
        for item in set:
            movie = items_dict[item]
            movies.append (movie)
        print movies
    print "Total of {0} frequent itemsets over threshold {2} found in {1} s".format(i, (end-start)/1000, threshold)
    print "=========\n"
    print "end of part II:\n"

if __name__ == '__main__':
    main()