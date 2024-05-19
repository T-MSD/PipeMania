# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 102613 Tiago Miguel Santos Dias
# 103037 Tiago Coutinho Carreto Tavares Rebelo

import sys
import copy
import random
from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class PipeManiaState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = PipeManiaState.state_id
        PipeManiaState.state_id += 1
        
        self.hash = self.compute_hash()

    def __lt__(self, other):
        return self.id < other.id

    def __eq__(self, value: object) -> bool:
        isEqual = isinstance(value, PipeManiaState) and self.board == value.board
        return isEqual
    
    def compute_hash(self):
        board = self.board.board
        otherBoard = []
        for row in board:
            otherBoard.append(tuple(row))
            
        otherBoard = tuple(otherBoard)
        return hash(otherBoard)
        
    def __hash__(self) -> int:
        return self.hash
        

class Board:
    """Representação interna de um tabuleiro de PipeMania."""
    def __init__(self, board):
        self.board = board
                
        self.locked = {(row, col): False for row in range(len(self.board)) for col in range(len(self.board))}

    @property
    def dim(self):
        return len(self.board)
    
    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return self.board[row][col]

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""
        up = self.board[row - 1][col] if row > 0 else None
        down = self.board[row + 1][col] if row < len(self.board[col]) - 1 else None
        return up, down

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respectivamente."""
        left = self.board[row][col - 1] if col > 0 else None
        right = self.board[row][col + 1] if col < len(self.board[row]) - 1 else None
        return left, right
    

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board."""
        if DEBUG:
            lines = DEBUG_BOARD
        else:
            lines = sys.stdin.readlines()
        
        board = []
        for row in lines:
            row = row.strip().split("\t")
            board.append(row)
            
        return Board(board)

    # TODO: outros metodos da classe
    def print_board(self):
        #for row in self.board:
            #print(row)
            
        formatted_output = '\n'.join([' '.join(row) for row in self.board])
        print(formatted_output)
            
            
    def __eq__(self, value: object) -> bool:
        isEqual = isinstance(value, Board) and self.board == value.board
        return isEqual

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        
        self.initial = PipeManiaState(board)
        self.dim = board.dim
        
        self.type = {
            "F" : ["FC", "FD", "FB", "FE"],
            "V" : ["VC", "VD", "VB", "VE"],
            "B" : ["BC", "BD", "BB", "BE"],
            "L" : ["LH", "LV"]
        }
        
        
        self.rotations ={
            "FC" : ["FD", "FE"],
            "FD" : ["FB", "FC"],
            "FB" : ["FE", "FD"],
            "FE" : ["FC", "FB"],
            
            "BC" : ["BD", "BE"],
            "BD" : ["BB", "BC"],
            "BB" : ["BE", "BD"],
            "BE" : ["BC", "BB"],
            
            "VC" : ["VD", "VE"],
            "VD" : ["VB", "VC"],
            "VB" : ["VE", "VD"],
            "VE" : ["VC", "VB"],
            
            "LH" : ["LV", "LV"],
            "LV" : ["LH", "LH"]
            }
        
        self.above = ["FC", "BC", "BE", "BD", "VC", "VD", "LV"]
        self.under = ["FB", "BB", "BE", "BD", "VB", "VE", "LV"]
        self.AtRight = ["FD", "BD", "BC", "BB", "VD", "VB", "LH"]
        self.AtLeft = ["FE", "BE", "BC", "BB", "VE", "VC", "LH"]
        
    def checkUpConnection(self, state, row, col):
        up, down = state.board.adjacent_vertical_values(row, col)
        
        if up in self.under:
            return True
        
        return False

    def checkDownConnection(self, state, row, col):
        up, down = state.board.adjacent_vertical_values(row, col)
        
        if down in self.above:
            return True
        
        return False
    
    def checkRightConnection(self, state, row, col):
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        if right in self.AtLeft:
            return True
        
        return False
    
    def checkLeftConnection(self, state, row, col):
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        if left in self.AtRight:
            return True
        
        return False
        
    
    def checkBorderActions(self, value, row, col):
        
        
        if row == 0 and col == 0 and value == "VC":
            _actions_list = []
            _actions_list.append((row, col, True))
            _actions_list.append((row, col, False))
            return set(_actions_list)
        
        if row == 0 and col == self.dim -1 and value == "VD":
            _actions_list = []
            _actions_list.append((row, col, True))
            _actions_list.append((row, col, False))
            return set(_actions_list)
        
        if row == self.dim -1 and col == 0 and value == "VE":
            _actions_list = []
            _actions_list.append((row, col, True))
            _actions_list.append((row, col, False))
            return set(_actions_list)
        
        if row == self.dim - 1 and col == self.dim - 1 and value == "VB":
            _actions_list = []
            _actions_list.append((row, col, True))
            _actions_list.append((row, col, False))
            return set(_actions_list)
        
        
            
        
        rotation = self.rotations[value]
        row_cases_to_check = [
            ("row", 0, self.above),
            ("row", self.dim - 1, self.under),
            ("col", 0, self.AtLeft),
            ("col", self.dim - 1, self.AtRight)
        ]
        
        
        
        actions_list = []
        for cell_type, cell, discardable_values in row_cases_to_check:
            same_cell = (cell_type == "row" and row == cell) or (cell_type == "col" and col == cell)
           
            if same_cell:
                _actions_list = []
                clockwise_rotation, counterclockwise_rotation = rotation
                if clockwise_rotation not in discardable_values:
                    _actions_list.append((row, col, True))
                if counterclockwise_rotation not in discardable_values:
                    _actions_list.append((row, col, False))
                
                actions_list.append(set(_actions_list))
                
            if len(actions_list) == 0:
                intersection_set = set()
            elif len(actions_list) == 1:
                intersection_set = set(actions_list[0])
            elif len(actions_list) == 2:
                intersection_set = set(actions_list[0]).intersection(actions_list[1])
                
        return intersection_set
    
    
    def checkAvailableConnectionActions(self, state, row, col):
        actions_list = []
        #se ha peca a volta que tenha conexao para peca que estamos, adicionamos rota;ao
        if (self.checkUpConnection(state, row, col) or self.checkDownConnection(state, row, col) 
                    or self.checkLeftConnection(state, row, col) or self.checkRightConnection(state, row, col)):
                    actions_list.append((row, col, True))
                    actions_list.append((row, col, False))
    
        return set(actions_list)
    
    def checkStuckActions(self, state, row, col):
        actions_list = []
        #se nao ha nada a volta, rodar a peca para que as suas saidas estejam orientadas para outras pecas
        if (not self.checkUpConnection(state, row, col) and not self.checkDownConnection(state, row, col) 
                    and not self.checkLeftConnection(state, row, col) and not self.checkRightConnection(state, row, col)):
                    actions_list.append((row, col, True))
                    actions_list.append((row, col, False))
        
        return set(actions_list)
    
        
    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
            
        actions_list = []

        for row in range(state.board.dim):
            for col in range(state.board.dim):
                value = state.board.get_value(row, col)
                
                
                if not state.board.locked[(row, col)]:
                    #actions_list.append((row, col, True))
                    #actions_list.append((row, col, False))
                
                
                    if row == 0 or col == 0 or row == state.board.dim - 1 or col == state.board.dim - 1:
                        border_set = self.checkBorderActions(value, row, col)
                        actions_list.extend(list(border_set))
                        
                    else:
                        available_set = self.checkAvailableConnectionActions(state, row, col)
                        stuck_set = self.checkStuckActions(state, row, col)
                        actions_list.extend(list(available_set))
                        actions_list.extend(list(stuck_set))    

                
        #random.shuffle(actions_list)   
        #print(actions_list)     
        return actions_list
    
    def readyToBeLocked(self, state, row, col):
        
        #eu tenho de ver ocmo faco estas pecas pararem de rodar porque se nao fica presa na mesma
        value = state.board.get_value(row, col)      
        up, down = state.board.adjacent_vertical_values(row, col)
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        if value == "FB":
            if down == None:
                return False

        elif value == "FC":
            if up == None:
                return False
            
        elif value == "FE":
            if left == None:
                return False
            
        elif value == "FD":
            if right == None:
                return False
            
        elif value == "BB":
            if down not in self.above or right not in self.AtLeft or left not in self.AtRight:
                return False
            
        elif value == "BC":
            if up not in self.under or right not in self.AtLeft or left not in self.AtRight:
                return False
        
        elif value == "BE":
            if up not in self.under or down not in self.above or left not in self.AtRight:
                return False
            
        elif value == "BD":
            if up not in self.under or right not in self.AtLeft or down not in self.above:
                return False
            
        elif value == "VC":
            if up == None or left == None:
                return False
            
        elif value == "VB":
            if down == None or right == None:
                return False
            
        elif value == "VE":
            if down == None or left == None:
                return False
            
        elif value == "VD":
            if up == None or right == None:
                return False
            
        elif value == "LH":
            if right not in self.AtLeft or left not in self.AtRight:
                return False
            
        elif value == "LV":
            if up not in self.under or down not in self.above:
                return False

        return True
        
        
        
        
    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
    
        row, col, direction = action
        value = state.board.get_value(row, col)
        rotation = self.rotations[value]
        
        
        
        new_Board = copy.deepcopy(state.board)
        
        if direction:
            new_Board.board[row][col] = rotation[0]
        
        
            
        if (self.readyToBeLocked(state, row, col)):
            new_Board.locked[(row, col)] = True
    
        print("----====----")
        new_Board.print_board()
        print("----====----")

        return PipeManiaState(new_Board)
        
                    
                    
                
                

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema.""" 
        

        
        for row in range(state.board.dim):
            for col in range(state.board.dim):
                value = state.board.get_value(row, col)
                              
                
                up, down = state.board.adjacent_vertical_values(row, col)
                left, right = state.board.adjacent_horizontal_values(row, col)
                
                if value == "FB":
                    if down not in self.above:
                        return False

                elif value == "FC":
                    if up not in self.under:
                        return False
                    
                elif value == "FE":
                    if left not in self.AtRight:
                        return False
                    
                elif value == "FD":
                    if right not in self.AtLeft:
                        return False
                    
                elif value == "BB":
                    if down not in self.above or right not in self.AtLeft or left not in self.AtRight:
                        return False
                    
                elif value == "BC":
                    if up not in self.under or right not in self.AtLeft or left not in self.AtRight:
                        return False
                
                elif value == "BE":
                    if up not in self.under or down not in self.above or left not in self.AtRight:
                        return False
                    
                elif value == "BD":
                    if up not in self.under or right not in self.AtLeft or down not in self.above:
                        return False
                    
                elif value == "VC":
                    if up not in self.under or left not in self.AtRight:
                        return False
                    
                elif value == "VB":
                    if down not in self.above or right not in self.AtLeft:
                        return False
                    
                elif value == "VE":
                    if down not in self.above or left not in self.AtRight:
                        return False
                    
                elif value == "VD":
                    if up not in self.under or right not in self.AtLeft:
                        return False
                    
                elif value == "LH":
                    if right not in self.AtLeft or left not in self.AtRight:
                        return False
                    
                elif value == "LV":
                    if up not in self.under or down not in self.above:
                        return False

        return True

    
    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass
    
        #ligacoes / total de ligacoes possivel e inverter * -1
        
        
        #pegar em cada peca ver a ligacao que precisa e se nao houver ligacoes do outro lado e usar logo isso

    # TODO: outros metodos da classe


if __name__ == "__main__":
    DEBUG = False
    DEBUG_BOARD = [
        "VC	VD",
        "FB	FB"
    ]
    # Ler grelha do figura 1a:
    board = Board.parse_instance()
    # Criar uma instância de PipeMania:
    problem = PipeMania(board)
    # Obter o nó solução usando a procura em profundidade:
    goal_node = depth_first_tree_search(problem)
    # Verificar se foi atingida a solução
    #print("asdasdasdasd: ", problem.actions(goal_node.state.board.actions))
    #print("Is goal?", problem.goal_test(goal_node.state))
    goal_node.state.board.print_board()
    
    # Verificar se foi atingida a solução
    #print("Is goal?", problem.goal_test(s1))
    #print("Is goal?", problem.goal_test(s2))
    #print("Solution:\n", s2.board.print_board(), sep="")