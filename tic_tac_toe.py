from time import time
import sys,random,signal,copy
from operator import itemgetter


class Team26():

    def __init__(self):
        self.starttime = 0
        self.endtime = 15.98
        self.MAX = 10000000       
        self.MIN = -10000000
        self.initial_level = 2
        self.upper = [-1, 0, 1, 0]
        self.current_player = 1
        self.lower = [0, 1, 0, -1]
        self.player_symbol = ['o', 'x']
        self.increment_cost = [0,2, 200, 20000, 200000]


    def move(self, board, old_move, flag):


        if flag == 'x': 
            player = self.current_player = 1
        else:   
            player = self.current_player = 0

        self.starttime = time()
        
        #variable for checking u have time for going one level deeper than current
        self.have_time = 'YES'

        #intializing the depth
        depth = self.initial_level
        depth_increment = 1
        #taking the worst case
        current_max = self.MIN
        available_moves = board.find_valid_move_cells(old_move)
        final_move = available_moves[random.randrange(len(available_moves))]

        while time() - self.starttime < self.endtime:
            move = self.move_minimax(board, old_move, player, depth)
            #If time permits increase the search by one level
            if self.have_time == 'YES':        
                final_move = move #updating current best move
                depth = depth + depth_increment

        #again make it YES for next move
        self.have_time = 'YES'
        return final_move

    def move_minimax(self, board, old_move, player, level):

        available_moves = board.find_valid_move_cells(old_move)
        #choose some random move to be best one
        best_move = available_moves[random.randrange(len(available_moves))]
        current_max = self.MIN

        for i_move in range(len(available_moves)):
            value = self.move_ab_minimax(level, player ^ 1, available_moves[i_move], 
                                 self.MIN, self.MAX, board)
            if value > current_max:
                current_max = value
                best_move = available_moves[i_move]
        return best_move
    

    def move_ab_minimax(self, level, player, old_move, alpha, beta, board):

        avaliable_moves = board.find_valid_move_cells(old_move)        
        if time() - self.starttime > self.endtime:
            self.have_time = 'NO'
            return -1

        if level == 0 or board.find_terminal_state() != ('CONTINUE', '-'):
            return self.heuristic(board, self.current_player)

        if self.have_time == 'NO':
            return -1

        value = self.MAX
        if (player == self.current_player):
            value = self.MIN

        for i_move in range(len(avaliable_moves)):

            if self.have_time == 'NO':
                break

            board.update(old_move, avaliable_moves[i_move], self.player_symbol[player])
            
            if player != self.current_player:
                value = min(value, self.move_ab_minimax(
                    level-1, player ^ 1, avaliable_moves[i_move], alpha, beta, board))
                board.board_status[avaliable_moves[i_move][0]][avaliable_moves[i_move][1]] = "-"
                board.block_status[avaliable_moves[i_move][0]/4][avaliable_moves[i_move][1]/4] = "-"
                beta = min(value, beta)

            else:
                value = max(value, self.move_ab_minimax(
                    level-1, player ^ 1, avaliable_moves[i_move], alpha, beta, board))
                board.board_status[avaliable_moves[i_move][0]][avaliable_moves[i_move][1]] = "-"
                board.block_status[avaliable_moves[i_move][0]/4][avaliable_moves[i_move][1]/4] = "-"
                alpha = max(alpha, value)
                
            if (alpha >= beta):
                break;

        return value

    def heuristic(self, board, player):

        player_0 = self.player_symbol[player]
        player_1 = self.player_symbol[player ^ 1]
        cur_state = board.find_terminal_state()
        check = cur_state[1]
        if check == "WON":
            if self.current_player != player:
                return self.MIN
            else:
             return self.MAX
        cost = []
        for i in range(4):
            cost.append([0,0,0,0])
        rows = columns =4
        for i in range(rows):
            for j in range(columns):
                status = board.block_status[i][j]
                if (status == player_1):
                    computing_cost = self.MIN/16
                    cost[i][j] = computing_cost
                elif(status == player_0):
                    computing_cost = self.MAX/16;
                    cost[i][j] = computing_cost
                else:
                    computing_cost = self.compute_block_cost(board, player, i, j)
                    cost[i][j] = computing_cost

        return self.compute_big_board(board,player, cost)

    def compute_big_board(self, board, player, cost):
    	flag = 0 
        player_0 = self.player_symbol[player]
        player_1 = self.player_symbol[player ^ 1]
        rowsize = colsize =4
        row = []
        col = []
        col_total = [0,0,0,0]
        row_total = [0,0,0,0]

        total = 0
        for i in range(4):
            row.append([])

        for i in range(4):    
            col.append([])


        for i in range(4):
            for j in range(4):
                status = board.block_status[i][j]
                row[i].append(status)
                col[j].append(status)
                col_total[j] = col_total[j] + cost[i][j]
                row_total[i] = row_total[i] + cost[i][j]


        for i in xrange(0,4):
            current_mx_row = row[i].count(player_0)
            current_mx_col = col[i].count(player_0)
            current_mn_row = row[i].count(player_1)
            current_mn_col = col[i].count(player_1)
            current_emp_row = col[i].count('-')
            current_emp_col = col[i].count('-')
            if (current_mx_row + current_emp_row == rowsize):
                total += row_total[i]
            if (current_mx_col + current_emp_col == colsize):
                total += col_total[i]
            if(current_mn_col + current_emp_col == colsize):
                total += col_total[i]
            if(current_mn_row + current_emp_row == rowsize):
                total += row_total[i]  
                flag = 1   
		           

        for i in xrange(1,3):
            for j in xrange(1,3):
                flag =0 
                current_mx = current_mn = current_emp = summ = 0
                for k in range(4):
                    i_x = self.upper[k]+i
                    j_x = self.lower[k]+j
                    temp = board.block_status[i_x][j_x]
                    if temp == player_1:
                        current_mn += 1
                    elif temp == player_0:
                        current_mx += 1
                    elif temp == "-":
                        current_emp += 1

                    index_i = self.upper[k] + i
                    index_j = self.lower[k] + j
                    summ += cost[index_i][index_j]
                
                if (current_mx+current_emp == 4):
                    total += summ
                if(current_mn + current_emp == 4):
                    total += summ 


        return total




    def compute_block_cost(self, board, player, row_no, col_no):

        player_0 = self.player_symbol[player]
        player_1 = self.player_symbol[player ^ 1]
        row = []
        total = 0        
        col = []
        for i in range(4):
            row.append([])

        for i in range(4):
            col.append([])
        
        total = 0

        rowsize = 4*row_no
        colsize = 4*col_no

        for i in range(rowsize, rowsize + 4):
            for j in range(colsize, colsize + 4):
                status = board.board_status[i][j]
                row[i%4].append(status)
                col[j%4].append(status)

        for i in range(4):
            
            current_mx_row = row[i].count(player_0)
            current_mx_col = col[i].count(player_0)
            current_mn_row = row[i].count(player_1)
            current_mn_col = col[i].count(player_1)

            if (current_mx_row == 0 and current_mn_row > 0):
                total -= self.increment_cost[current_mn_row]
            elif(current_mx_row > 0 and current_mn_row == 0):
                total += self.increment_cost[current_mx_row]

            if (current_mx_col == 0 and current_mn_col > 0):
                total -= self.increment_cost[current_mn_col]
            elif (current_mx_col > 0 and current_mn_col == 0):
                total += self.increment_cost[current_mx_col]
        
        for i in xrange(1,3):
            for j in xrange(1,3):

                current_mx = current_mn = flag = 0
                for k in range(4):
                    i_x = rowsize + self.upper[k]+i
                    j_x = colsize + self.lower[k]+j
                    temp = board.board_status[i_x][j_x] 
                    if temp == player_1:
                        current_mn += 1
                        flag = 0
                    elif temp == player_0:
                        flag = 1
                        current_mx += 1
    
                if (current_mn > 0 and current_mx == 0):
                    total -= self.increment_cost[current_mn]  
                elif (current_mn == 0 and current_mx > 0):
                    total += self.increment_cost[current_mx]
        return total