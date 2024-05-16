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
    depth_first_graph_search
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
        down = self.board[row + 1][col] if row < len(self.board) - 1 else None
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
        for row in self.board:
            print(row)
            
    def __eq__(self, value: object) -> bool:
        isEqual = isinstance(value, Board) and self.board == value.board
        return isEqual

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        
        self.initial = PipeManiaState(board)
        self.board = self.initial 
        
        #self.total_rotations = {(row, col): 0 for row in range(board.dim) for col in range(board.dim)}
        
        #self.visited_states = []
        
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
        
        
        
    def rotateInvalidConnection(self, state: PipeManiaState, row, col):
        
        value = state.board.get_value(row, col)
        up, down = state.board.adjacent_vertical_values(row, col)
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        #se a peca tiver na sua baertura a peca que encaixa, retorna false
        #se nao tiver  uma peca que encaixe retorna verdadeio para ser criada uma acao que rode essa peca

        connections = {
            "FB": lambda: down not in self.above,
            "FC": lambda: up not in self.under,
            "FE": lambda: left not in self.AtRight,
            "FD": lambda: right not in self.AtLeft,
            "BB": lambda: down not in self.above or right not in self.AtLeft or left not in self.AtRight,
            "BC": lambda: up not in self.under or right not in self.AtLeft or left not in self.AtRight,
            "BE": lambda: up not in self.under or down not in self.above or left not in self.AtRight,
            "BD": lambda: up not in self.under or right not in self.AtLeft or down not in self.above,
            "VC": lambda: up not in self.under or left not in self.AtRight,
            "VB": lambda: down not in self.above or right not in self.AtLeft,
            "VE": lambda: down not in self.above or left not in self.AtRight,
            "VD": lambda: up not in self.under or right not in self.AtLeft,
            "LH": lambda: right not in self.AtLeft or left not in self.AtRight,
            "LV": lambda: up not in self.under or down not in self.above
        }

        if value in connections:
            if connections[value]():
                return True
        return False
    
    def rotateStuck(self, state: PipeManiaState, row, col):
        #rodar se a volta que liga a peca do meio
        value = state.board.get_value(row, col)
        up, down = state.board.adjacent_vertical_values(row, col)
        left, right = state.board.adjacent_horizontal_values(row, col)
        
        nearby = [up, down, left, right]
        
        connections = {
            "FB": lambda: down not in self.above,
            "FC": lambda: up not in self.under,
            "FE": lambda: left not in self.AtRight,
            "FD": lambda: right not in self.AtLeft,
            "BB": lambda: down not in self.above or right not in self.AtLeft or left not in self.AtRight,
            "BC": lambda: up not in self.under or right not in self.AtLeft or left not in self.AtRight,
            "BE": lambda: up not in self.under or down not in self.above or left not in self.AtRight,
            "BD": lambda: up not in self.under or right not in self.AtLeft or down not in self.above,
            "VC": lambda: up not in self.under or left not in self.AtRight,
            "VB": lambda: down not in self.above or right not in self.AtLeft,
            "VE": lambda: down not in self.above or left not in self.AtRight,
            "VD": lambda: up not in self.under or right not in self.AtLeft,
            "LH": lambda: right not in self.AtLeft or left not in self.AtRight,
            "LV": lambda: up not in self.under or down not in self.above
        }
        
        for piece in nearby:
            if piece in connections:
                if connections[piece]():
                    return True
            return False
        

    def checkBordersClockwise(self, state, row, col):
        value = state.board.get_value(row, col)
            
        rotation = self.rotations[value]
        
        print(value)
        print(rotation)
            
        if row == 0:
            if rotation[0] in self.above:
                return "notBorder"
            
        if row == state.board.dim - 1:
            if rotation[0] in self.under:
                return "notBorder"
           
        if col == 0:
            if rotation[0] in self.AtLeft:
                return "notBorder"
            
            
        if col == state.board.dim - 1:
            if rotation[0] in self.AtRight:
                return "notBorder"
          
        return "Clockwise"
        
    def checkBordersCounterclockwise(self, state, row, col):
        value = state.board.get_value(row, col)
            
        rotation = self.rotations[value]
            
        if row == 0:
            if rotation[1] in self.above:                
                return "notBorder"
    
            
        if row == state.board.dim - 1:
            if rotation[1] in self.under:
                return "notBorder"
            
            
        if col == 0:
            if rotation[1] in self.AtLeft:
                return "notBorder"
            
            
        if col == state.board.dim - 1:
            if rotation[1] in self.AtRight:
                return "notBorder"
            
        return "Counterclockwise"
    
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
        
        
    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        
        
        actions_list = []

        

        for row in range(state.board.dim):
            for col in range(state.board.dim):
                if (self.checkUpConnection(state, row, col) or self.checkDownConnection(state, row, col) 
                    or self.checkLeftConnection(state, row, col) or self.checkRightConnection(state, row, col)):
                    actions_list.append((row, col, True))
                    actions_list.append((row, col, False))
                
                elif (not self.checkUpConnection(state, row, col) and not self.checkDownConnection(state, row, col) 
                    and not self.checkLeftConnection(state, row, col) and not self.checkRightConnection(state, row, col)):
                    actions_list.append((row, col, True))
                    actions_list.append((row, col, False))
                    
                    
        
        random.shuffle(actions_list)
        print(actions_list)
        return actions_list
        
    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
    
        row, col, direction = action
        value = state.board.get_value(row, col)
        rotation = self.rotations[value]
        
        new_board = copy.deepcopy(state.board.board)
        
        if direction:
            new_board[row][col] = rotation[0]
        
        else:
            new_board[row][col] = rotation[1]
                
                
        #if new_state.board in self.visited_states:
            #return None

        #self.visited_states.append(new_state.board)
        new_Board = Board(new_board)
        new_state = PipeManiaState(new_Board)
        
        #print("----====----")
        #new_Board.print_board()
        #print("----====----")

        return new_state
        
                    
                    
                
                

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
                        print('1')
                        return False

                elif value == "FC":
                    if up not in self.under:
                        print('2')
                        return False
                    
                elif value == "FE":
                    if left not in self.AtRight:
                        print('3')
                        return False
                    
                elif value == "FD":
                    if right not in self.AtLeft:
                        print('4')
                        return False
                    
                elif value == "BB":
                    if down not in self.above or right not in self.AtLeft or left not in self.AtRight:
                        print('5')
                        return False
                    
                elif value == "BC":
                    if up not in self.under or right not in self.AtLeft or left not in self.AtRight:
                        print('6')
                        return False
                
                elif value == "BE":
                    if up not in self.under or down not in self.above or left not in self.AtRight:
                        print('7')
                        return False
                    
                elif value == "BD":
                    if up not in self.under or right not in self.AtLeft or down not in self.above:
                        print('8')
                        return False
                    
                elif value == "VC":
                    if up not in self.under or left not in self.AtRight:
                        print('9')
                        return False
                    
                elif value == "VB":
                    if down not in self.above or right not in self.AtLeft:
                        print('10')
                        return False
                    
                elif value == "VE":
                    if down not in self.above or left not in self.AtRight:
                        print('11')
                        return False
                    
                elif value == "VD":
                    if up not in self.under or right not in self.AtLeft:
                        print('12')
                        return False
                    
                elif value == "LH":
                    if right not in self.AtLeft or left not in self.AtRight:
                        print('13')
                        return False
                    
                elif value == "LV":
                    if up not in self.under or down not in self.above:
                        print('14')
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
    DEBUG = True
    DEBUG_BOARD = [
        "FE	FD",
        "VE	VB"
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
    print("SUCCESS: ")
    goal_node.state.board.print_board()
    
    # Verificar se foi atingida a solução
    #print("Is goal?", problem.goal_test(s1))
    #print("Is goal?", problem.goal_test(s2))
    #print("Solution:\n", s2.board.print_board(), sep="")