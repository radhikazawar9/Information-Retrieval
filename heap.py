"""
Assignment 2 Group 12

Radhika Zawar s3734939
Parvi Verma s3744398
"""

import heapq

# Source http://joernhees.de/blog/2010/07/19/min-heap-in-python/
# used heapq as it has very optimised operation

"""
To calculate Top N ranked documents
"""

def HeapifyList(hash_acc,num_ranks):

    # Building Intial Heap with starting n elements
    # Note: size of heap is equal to number of top ranked documents
    for values in hash_acc.values()[0:num_ranks]:
        heapList.append(values)

    length = len(heapList)

    # The loop starts halfway along the list of items to skip subheaps of size 1
    for i in reversed(range(length//2)):
        Heapify(heapList, i)

    # for each id from starting from n till length of hash table
    for id in hash_acc.keys()[num_ranks:len(hash_acc)]:
        root = heapList[0]                      # root: minimum item of heap at 0th position of list
        if hash_acc[id] > root:                 # if accumulater is greater than root
            heapList[0] = hash_acc[id]          # then replace root with accumulator
        for i in reversed(range(length//2)):    # calling function to re-heapify the list
            Heapify(heapList, i)

    sorted_list = []                            # To store sorted heap
    for element in reversed(range(num_ranks)):  # Sorting the heap in ascending order
        if not heapList:                        #if heap list is empty
            break                               # exit the loop
        sorted_list.append(min(heapList))       # appending min heap element to sorted list
        heapList.remove(min(heapList))          # deleting min element from heap

    return sorted_list

"""
Applying Min Heap
"""

def Heapify(heapList, pos):
    endpos = len(heapList)
    child_pos = 2*pos + 1                                                       #child_pos = left child

    while child_pos < endpos:

        right_pos = child_pos + 1                                               # right child
        if right_pos < endpos and heapList[child_pos] > heapList[right_pos]:    #if pos has two children, check if left or right is smaller
            child_pos =  right_pos

        if heapList[pos] <= heapList[child_pos]:                                # if pos < smaller child
            break                                                               # exit loop


        temp = heapList[pos]                                                    # else swap pos and smaller child
        heapList[pos] =  heapList[child_pos]
        pos = child_pos
        child_pos = 2*pos + 1
        heapList[pos] = temp



"""
minHeap data structure to select the top n accumulators
of highest similarity index
"""
class Heap(object):

    def __init__(self):     #creating heap
        self._heap = []

    def push(self, priority, item, replace=False):      #adding data in the heap
        assert priority >= 0                            # 0 is the highest Priority thus it would be popped first

        if replace and self._heap:                      # Remove smallest element
            if priority > self._heap[0][0]:             # check if it is not the smallest
                heapq.heapreplace(self._heap, (priority, item)) # insert, removing _heap[0]
        else:
            heapq.heappush(self._heap, (priority, item)) # if smallest push changes

    def pop(self):                                      # popping highest priority
        item = heapq.heappop(self._heap)[1]             # (prio, item)[1] == item
        return item

    def __len__(self):                                  # finds leghth
        return len(self._heap)

    def __iter__(self):                                 # ierator
        return self

    def next(self):                                     # lowest first, saving by priority
        try:
            return self.pop()
        except IndexError:
            raise StopIteration
