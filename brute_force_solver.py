#!/usr/bin/env python
# coding: utf-8

# In[62]:


#python sudoku driver

import numpy as np

def make_board():
    with open("board.txt") as f:
        return np.array(list(map(lambda line: list(line.strip()), f.readlines()))).astype("int64")

board = make_board()

if len(board) != 9 or len(board[0]) != 9:
    raise Exception('Board must be 9x9.')

def make_tiles():
    tiles = [0]*9
    for i in range(3):
        tiles[i] = np.array((board[0:3, 0 + i*3:3 + i *3]))
        tiles[i + 3] = np.array((board[3:6, 0 + i*3:3 + i *3]))
        tiles[i + 6] = np.array((board[6:9, 0 + i*3:3 + i *3]))
    return np.array((tiles))

tiles = make_tiles()

def make_unknowns():
    unknowns = []
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                unknowns.append((i,j))
    return unknowns

unknowns = make_unknowns()
    
def board_to_tile_coords(m,n):
    return (what_tile(m,n), int(np.piecewise(m, [m in (0,1,2), m in (3,4,5), m in (6,7,8)],                  [lambda m: m, lambda m: m - 3, lambda m: m - 6])),             int(np.piecewise(n, [n in (0,1,2), n in (3,4,5), n in (6,7,8)],                  [lambda n: n, lambda n: n - 3, lambda n: n - 6])))
    
def update(m,n,updated_value):
    tile_coords = board_to_tile_coords(m,n)
    tiles[tile_coords[0]][tile_coords[1]][tile_coords[2]] = updated_value
    board[m][n] = updated_value
    
#returns index of a tile in the tiles arr
def what_tile(m,n):
    tile_map = np.array(([0,1,2],[3,4,5],[6,7,8]))
    x,y = int(np.floor(m / 3)), int(np.floor(n / 3))
    return tile_map[x][y]
    
#return the list of valid numbers, given coords
#the current number (if nonzero) is considered valid
def avail_nums(m,n): 
    tile = what_tile(m,n)
    a = set(board[m].tolist() + board[:,n].tolist() + np.reshape(tiles[tile], 9).tolist())
    b = {1,2,3,4,5,6,7,8,9}
    if board[m][n] != 0:
        c = sorted(b.difference(a)) + [board[m][n]]
    else:
        c = b.difference(a)
    return sorted(c)

#returns the next-largest legal number for a square. only call next_avail when there is such a number
def next_avail(m,n,curr_val):
    avail = avail_nums(m,n)
    if curr_val == 0:
        return avail[0]
    elif curr_val != 0 and avail.index(curr_val) < len(avail) - 1:
        at = avail.index(curr_val)
        return avail[at + 1]

#returns boolean for whether the value in a given square is the greatest legal number
def is_max(m,n,curr_val):
    avail = avail_nums(m,n)
    if 0 <= avail.index(curr_val) < (len(avail) - 1):
        return False
    elif avail.index(curr_val) == len(avail) - 1:
        return True

def final_check():
    num = 0
    ideal = {1,2,3,4,5,6,7,8,9}
    test = lambda x: set(board)
    for i in range(6): 
        if set(board[i]).difference(ideal) == set() and set(board[:,i]).difference(ideal) == set() and         set(list(tiles[i][0]) + list(tiles[i][1]) + list(tiles[i][2])).difference(ideal) == set():
             num+= 1
    for i in range(6,9):
        if set(board[i]).difference(ideal) == set() and set(board[:,i]).difference(ideal) == set():
            num += 1
    if num != 9:
        raise Exception('🤷')
    return True

#-----------UNUSED FCNS------------------------

# def check_space(m,n):   
#     num = board[m][n]
#     tile_in = what_tile(m,n)
#     m_count = list(board[m]).count(num)
#     n_count = list(board[:,n]).count(num)
#     tile_count = 0
#     for i in range(3):
#         tile_count += list(tiles[tile_in][i]).count(num)
#     if m_count > 1 or n_count > 1 or tile_count > 1:
#         return False
#     else:
#         return True

# def is_empty(thing):
#     return not len(thing)

#------program seems to run a little slower with the updated version of this one ??
# def board_to_tile_coords(m,n):
#     tile = what_tile(m,n)
#     if tile in range(3):
#         row = m
#     elif tile in range(3,6):
#         row = m - 3
#     else:
#         row = m - 6
#     if tile in (0,3,6):
#         col = n
#     elif tile in (1,4,7):
#         col = n - 3
#     else:
#         col = n - 6
#     return (tile, row, col)


# In[64]:


#backtracking algo - brute force

from IPython.display import clear_output
import time
start = time.time()
j = 0# last-changed square counter
(m,n) = unknowns[j]
run = 0
print_freq = 500 #larger ==> less frequent

while True:
    if board[m][n] == 0 and len(avail_nums(m,n)) > 0: #forward - succeed
        update(m,n,next_avail(m,n,board[m][n]))
        j += 1
        if j < len(unknowns):
            (m,n) = unknowns[j]
        else:
            break
    elif board[m][n] == 0 and len(avail_nums(m,n)) == 0: # forward - fail
        j -= 1
        (m,n) = unknowns[j]
    elif is_max(m,n,board[m][n]) == False: #backward - succeed
        update(m,n,next_avail(m,n,board[m][n]))
        j += 1
        (m,n) = unknowns[j]
    else: #backward - fail
        update(m,n,0)
        if j > 0:
            j -= 1
        (m,n) = unknowns[j]
#     uncomment below to see the board update as it runs. 
    run += 1
    if run % print_freq == 0:
        clear_output(wait=True)
        print(board, run)    
end = time.time()
final_check()
clear_output(wait=True)            
print(board)
print("took only " + str(end - start) + " secs in " + str(run) + " runs")
print("😼 ")

