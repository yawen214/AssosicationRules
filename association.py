""" 
assoication.py by Yawen Chen & Brian Charous 
for CS324 Winter 2015
PART I of Association Rule Assignment

To compile:
python -s --threshold -f itemsets -d datasets
for example: python association.py -s 1000 -f movies.dat -d ratings.dat
(finds all freq itemsets in size of 1 with support no less than the threshold 1000 in transactions in ratings.dat )
"""

import sys
import argparse
import time

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

def support_threshold_select (threshold, items_sets, transactions_list):
    ''' Return itemset of size one with support larger or equal to the threshold.
        Current version only return k =1 size freq items
    '''
    freq_itemsets = set()
    for item in items_sets:   
        count = 0
        for transaction in transactions_list:        
            if int(item) in transaction: #version 0: only care about k =1
                count += 1
        if count >= threshold:
            freq_itemsets.add(item)
    return freq_itemsets

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
    freq_itemsets = support_threshold_select(threshold, all_items_set, transactions_list)
    end = time.time()
    sys.stdout.write(" done in {0}ms\n\nFound:\n".format(end-start))
    print ("frequent items above threshold {0} found:").format(threshold)
    i = 0
    for items in freq_itemsets:
        i+= 1
        movie = items_dict[int(items)]
        print movie
    print "Total of {0} movies found in {1} s".format(i, (end-start)/1000)

    print "=========\n"
    print "end of part I:\n"

if __name__ == '__main__':
    main()