""" 
assoication.py by Yawen Chen & Brian Charous 
for CS324 Winter 2015
PART 2 of Association Rule Assignment

To run:
python -s --threshold -f itemsets -d datasets
for example: python association.py -s 1000 -f movies.dat -d ratings.dat
(finds all freq itemsets in size of 1 with support no less than the threshold 1000 in transactions in ratings.dat )
"""

import sys
import argparse
import time
import itertools

def get_items(filename):
    """ read in data from both the item file"""
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

def freq_item_generate (threshold, items_sets, transactions_list):
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
    # kepe track of last item
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--support_threshold', type= int, required=True, help='Input wanted support threshold')
    parser.add_argument('-f', '--items_file', required=True, help='The file name of the itemset')
    parser.add_argument('-d', '--dataset_file', required=True, help='The file name of the dataset')

    args = parser.parse_args()

    # Set up itemsets and datasets 
    sys.stdout.write("Working on seting up itemsets and datasets... ")
    sys.stdout.flush()
    threshold = int(args.support_threshold)
    items_dict, all_items_set = get_items(args.items_file)  # read in all itemsets
    transactions_list= get_transactions(args.dataset_file) # read in transactions and return set
    print(" done!")
    print "==========================="
    sys.stdout.write("Now working on finding freq_itemsets above threshold {0} with size of ...".format(threshold))
    sys.stdout.flush()
    start = time.time()
    freq_itemsets = freq_item_generate(threshold, all_items_set, transactions_list)
    end = time.time()
    sys.stdout.write(" done in {0}s\n\nFound:\n".format(end-start))
    print ("frequent items above threshold {0} found:").format(threshold)
    i = 0
    for items in freq_itemsets:
        i+= 1
        movie = items_dict[items]
        print movie
    print "Total of {0} movies found in {1} s".format(i, (end-start)/1000)

    print "=========\n"
    print "end of part I:\n"

if __name__ == '__main__':
    main()