# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 014:
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
    
    def getLockedUp(self, row, col):
        return self.locked[(row - 1, col)] if row > 0 else None
    
    def getLockedDown(self, row, col):
        return self.locked[(row + 1, col)] if row < len(self.board[col]) - 1 else None
    
    def getLockedRight(self, row, col):
        return self.locked[(row, col + 1)] if col < len(self.board[row]) - 1 else None
    
    def getLockedLeft(self, row, col):
        return self.locked[(row, col - 1)] if col > 0 else None

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

    def print_board(self):            
        formatted_output = '\n'.join(['\t'.join(row) for row in self.board])
        print(formatted_output)
            
    def __eq__(self, value: object) -> bool:
        isEqual = isinstance(value, Board) and self.board == value.board
        return isEqual

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        
        self.initial = PipeManiaState(board)
        self.dim = board.dim
    
        self.above = ["FC", "BC", "BE", "BD", "VC", "VD", "LV"]
        self.under = ["FB", "BB", "BE", "BD", "VB", "VE", "LV"]
        self.AtRight = ["FD", "BD", "BC", "BB", "VD", "VB", "LH"]
        self.AtLeft = ["FE", "BE", "BC", "BB", "VE", "VC", "LH"]
            
    def Instant_Actions(self):      
        #falta ver os casos dos F em que estao virados para uma peca locked e reduzir o numero de acoes   
        # Topo esquerdo
        if self.initial.board.board[0][0][0] == "V":  
            self.initial.board.board[0][0] = "VB"        
            self.initial.board.locked[(0, 0)] = True    
            
        # Topo direito
        if self.initial.board.board[0][self.dim - 1][0] == "V":  
            self.initial.board.board[0][self.dim - 1] = "VE"
            self.initial.board.locked[(0, self.dim - 1)] = True
              
        # Topo meio
        for col in range(1, self.dim):
            if self.initial.board.board[0][col][0] == "L":
                self.initial.board.board[0][col] = "LH"
                self.initial.board.locked[(0, col)] = True
                
            elif self.initial.board.board[0][col][0] == "B":
                self.initial.board.board[0][col] = "BB"
                self.initial.board.locked[(0, col)] = True
            
        # Baixo esquerdo
        if self.initial.board.board[self.dim - 1][0][0] == "V":  
            self.initial.board.board[self.dim - 1][0] = "VD"
            self.initial.board.locked[(self.dim - 1, 0)] = True
            
        # Baixo direito
        if self.initial.board.board[self.dim - 1][self.dim - 1][0] == "V":  
            self.initial.board.board[self.dim - 1][self.dim - 1] = "VC"
            self.initial.board.locked[(self.dim - 1, self.dim - 1)] = True
                        
        # Meio baixo
        for col in range(1, self.dim):
            if self.initial.board.board[self.dim - 1][col][0] == "L":
                self.initial.board.board[self.dim - 1][col] = "LH"
                self.initial.board.locked[(self.dim - 1, col)] = True
            
            elif self.initial.board.board[self.dim - 1][col][0] == "B":
                self.initial.board.board[self.dim - 1][col] = "BC"
                self.initial.board.locked[(self.dim - 1, col)] = True
            
        # Meio esquerda
        for row in range(1, self.dim - 1):
            if self.initial.board.board[row][0][0] == "L":
                self.initial.board.board[row][0] = "LV"
                self.initial.board.locked[(row, 0)] = True
            
            elif self.initial.board.board[row][0] == "B":
                self.initial.board.board[row][0] = "BD"
                self.initial.board.locked[(row, 0)] = True
            
        # Meio direita
        for row in range(1, self.dim - 1):
            if self.initial.board.board[row][self.dim - 1][0] == "L":
                self.initial.board.board[row][self.dim - 1] = "LV"
                self.initial.board.locked[(row, self.dim - 1)] = True
            
            elif self.initial.board.board[row][self.dim - 1][0] == "B":
                self.initial.board.board[row][self.dim - 1] = "BE"
                self.initial.board.locked[(row, self.dim - 1)] = True
                              
        #So para F aqui em baixo------------------------
        
        #canto sup esquerdo
        if self.initial.board.board[0][0][0] == "F":
            if self.initial.board.locked[(1, 0)] and self.initial.board.board[1][0] in self.above:
                self.initial.board.board[0][0] = "FB"
                self.initial.board.locked[(0, 0)] = True
            
            elif self.initial.board.locked[(0, 1)] and self.initial.board.board[0][1] in self.AtLeft:
                self.initial.board.board[0][0] = "FD"
                self.initial.board.locked[(0, 0)] = True 
              
        #canto sup direito  
        if self.initial.board.board[0][self.dim - 1][0] == "F":
            if self.initial.board.locked[(0, self.dim - 2)] and self.initial.board.board[0][self.dim - 2] in self.AtRight:
                self.initial.board.board[0][self.dim - 1] = "FE"
                self.initial.board.locked[(0, self.dim - 1)] = True
            
            elif self.initial.board.locked[(1, self.dim - 1)] and self.initial.board.board[1][self.dim - 1] in self.above:
                self.initial.board.board[0][self.dim - 1] = "FB"
                self.initial.board.locked[(0, self.dim - 1)] = True 
                
        #canto inf esquerdo
        if self.initial.board.board[self.dim - 1][0][0] == "F":
            if self.initial.board.locked[(self.dim - 2, 0)] and self.initial.board.board[self.dim - 2][0] in self.under:
                self.initial.board.board[self.dim - 1][0] = "FC"
                self.initial.board.locked[(self.dim - 1, 0)] = True
            
            elif self.initial.board.locked[(self.dim - 1, 1)] and self.initial.board.board[self.dim - 1][1] in self.AtLeft:
                self.initial.board.board[self.dim - 1][0] = "FD"
                self.initial.board.locked[(self.dim - 1, 0)] = True 
                
        #canto inf direito  
        if self.initial.board.board[self.dim - 1][self.dim - 1][0] == "F":
            if self.initial.board.locked[(self.dim - 2, self.dim - 1)] and self.initial.board.board[self.dim - 2][self.dim - 1] in self.under:
                self.initial.board.board[self.dim - 1][self.dim - 1] = "FC"
                self.initial.board.locked[(self.dim - 1, self.dim - 1)] = True
            
            elif self.initial.board.locked[(self.dim - 1, self.dim - 2)] and self.initial.board.board[self.dim - 1][self.dim - 2] in self.AtRight:
                self.initial.board.board[self.dim - 1][self.dim - 1] = "FE"
                self.initial.board.locked[(self.dim - 1, self.dim - 1)] = True 
                
        return
                
    def isBorder(self, row, col):
        return row == 0 or col == 0 or row == self.dim - 1 or col == self.dim - 1
        
    def doFinalActions(self, state, row, col, value):
        
        upLock = state.board.getLockedUp(row, col)
        downLock = state.board.getLockedDown(row, col)
        rightLock = state.board.getLockedRight(row, col)
        leftLock = state.board.getLockedLeft(row, col)
        
        up, down = state.board.adjacent_vertical_values(row, col)
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        actions_list = []
        
        if upLock or downLock or rightLock or leftLock:
            if value[0] == "F":
                if upLock and up in self.under:
                    actions_list.append((row, col, "FC"))
                
                if downLock and down in self.above:
                    actions_list.append((row, col, "FB"))
                
                if rightLock and right in self.AtLeft:
                    actions_list.append((row, col, "FD"))
                    
                if leftLock and left in self.AtRight:
                    actions_list.append((row, col, "FE"))
                    
                return actions_list
            
            if value[0] == "L":
                if upLock and up in self.under:
                    actions_list.append((row, col, "LV"))
                    
                if downLock and down in self.above:
                    actions_list.append((row, col, "LV"))
                
                if rightLock and right in self.AtLeft:
                    actions_list.append((row, col, "LH"))
                    
                if leftLock and left in self.AtRight:
                    actions_list.append((row, col, "LH"))
                    
                return actions_list
                    
            if value[0] == "V":
                if upLock and up in self.under:
                    actions_list.append((row, col, "VC"))
                    actions_list.append((row, col, "VD"))
                    
                if downLock and down in self.above:
                    actions_list.append((row, col, "VE"))
                    actions_list.append((row, col, "VB"))
                    
                if rightLock and right in self.AtLeft:
                    actions_list.append((row, col, "VD"))
                    actions_list.append((row, col, "VB"))
                    
                if leftLock and left in self.AtRight:
                    actions_list.append((row, col, "VC"))
                    actions_list.append((row, col, "VE"))
                    
                return actions_list
                    
            if value[0] == "B":
                if upLock and up in self.under:
                    actions_list.append((row, col, "BC"))
                    actions_list.append((row, col, "BE"))
                    actions_list.append((row, col, "BD"))
                    
                if downLock and down in self.above:
                    actions_list.append((row, col, "BB"))
                    actions_list.append((row, col, "BE"))
                    actions_list.append((row, col, "BD"))
                    
                if rightLock and right in self.AtLeft:
                    actions_list.append((row, col, "BB"))
                    actions_list.append((row, col, "BC"))
                    actions_list.append((row, col, "BD"))
                    
                if leftLock and left in self.AtRight:
                    actions_list.append((row, col, "BB"))
                    actions_list.append((row, col, "BE"))
                    actions_list.append((row, col, "BC"))
                
                return actions_list
                    
    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
            
        actions_list = []
        
        for row in range(state.board.dim):
            for col in range(state.board.dim):
                value = state.board.get_value(row, col)                
                if not state.board.locked[(row, col)]:
                    actions_list = self.doFinalActions(state, row, col, value)
                    
                    if actions_list:
                        return actions_list
                        
        return actions_list
        
    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
    
        row, col, new_value = action
        if not state.board.locked[(row, col)]:
            new_Board = copy.deepcopy(state.board)
            new_Board.board[row][col] = new_value
            new_Board.locked[(row, col)] = True
            return PipeManiaState(new_Board)
        
        return state
        
                    
                    
                
                

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
        "FC	VC	VC",
        "VC	BB	LH",
        "FE	VB	FD"
    ]
    board = Board.parse_instance()
    problem = PipeMania(board)
    problem.Instant_Actions()
    goal_node = depth_first_tree_search(problem)
    goal_node.state.board.print_board()