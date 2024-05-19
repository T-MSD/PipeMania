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
        
        self.types = {
            "F" : ["FC", "FD", "FB", "FE"],
            "V" : ["VC", "VD", "VB", "VE"],
            "B" : ["BC", "BD", "BB", "BE"],
            "L" : ["LH", "LV"]
        }
        
        
        self.rotations ={
            "FC" : ["FD", "FE", "FB"],
            "FD" : ["FB", "FC", "FE"],
            "FB" : ["FE", "FD", "FC"],
            "FE" : ["FC", "FB", "FD"],
            
            "BC" : ["BD", "BE", "BB"],
            "BD" : ["BB", "BC", "BE"],
            "BB" : ["BE", "BD", "BC"],
            "BE" : ["BC", "BB", "BD"],
            
            "VC" : ["VD", "VE", "VD"],
            "VD" : ["VB", "VC", "VE"],
            "VB" : ["VE", "VD", "VC"],
            "VE" : ["VC", "VB", "VD"],
            
            "LH" : ["LV", "LV", "LV"],
            "LV" : ["LH", "LH", "LH"]
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
        
    def checkRightBorderActions(self, value, row, col):
        actions_list = []

        # Topo esquerdo
        if row == 0 and col == 0:
            if value == 'FB':
                actions_list.append((row, col, 'FD'))
                return set(actions_list)
            elif value == 'FD':
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
        
        # Topo direito
        elif row == 0 and col == self.dim - 1:
            if value == 'FE':
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            elif value == 'FB':
                actions_list.append((row, col, 'FE'))
                return set(actions_list)
        
        # Topo meio
        elif row == 0 and col not in [0, self.dim - 1]:
           if value == 'FB':
               actions_list.append((row, col, 'FE'))
               actions_list.append((row, col, 'FD'))
               return set(actions_list)
           elif value == 'FE':
               actions_list.append((row, col, 'FB'))
               actions_list.append((row, col, 'FD'))
               return set(actions_list)
           elif value == 'FD':
               actions_list.append((row, col, 'FB'))
               actions_list.append((row, col, 'FE'))
               return set(actions_list)
           elif value == 'VB':
               actions_list.append((row, col, 'VE'))
               return set(actions_list)
           elif value == 'VE':
               actions_list.append((row, col, 'VB'))
               return set(actions_list)
            
        # Baixo esquerdo
        elif row == self.dim - 1 and col == 0:
            if value == 'FD':
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'FC':
                actions_list.append((row, col, 'FD'))
                return set(actions_list)
            
        # Baixo direito
        elif row == self.dim - 1 and col == self.dim - 1:
            if value == 'FE':
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'FC':
                actions_list.append((row, col, 'FE'))
                return set(actions_list)
        
        elif row == self.dim - 1 and col not in [0, self.dim - 1]:
            if value == 'FC':
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FE'))
                return set(actions_list)
            elif value == 'FD':
                actions_list.append((row, col, 'FC'))
                actions_list.append((row, col, 'FE'))
                return set(actions_list)
            elif value == 'FE':
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'VC':
                actions_list.append((row, col, 'VD'))
                return set(actions_list)
            elif value == 'VD':
                actions_list.append((row, col, 'VC'))
                return set(actions_list)
        
        # Lateral esquerda
        elif row not in [0, self.dim - 1] and col == 0:
            if value == 'FC':
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            elif value == 'FB':
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'FD':
                actions_list.append((row, col, 'FC'))
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            elif value == 'VB':
                actions_list.append((row, col, 'VD'))
                return set(actions_list)
            elif value == 'VD':
                actions_list.append((row, col, 'VB'))
                return set(actions_list)
          
        # Lateral direita
        elif row not in [0, self.dim - 1] and col == self.dim - 1:
            if value == 'FE':
                actions_list.append((row, col, 'FB'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'FC':
                actions_list.append((row, col, 'FB'))
                actions_list.append((row, col, 'FE'))
                return set(actions_list)
            elif value == 'FB':
                actions_list.append((row, col, 'FE'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            elif value == 'VC':
                actions_list.append((row, col, 'VE'))
                return set(actions_list)
            elif value == 'VE':
                actions_list.append((row, col, 'VC'))
                return set(actions_list)
        return set(actions_list)

    def checkWrongBorderActions(self, value, row, col, state: PipeManiaState):
        actions_list = []

        # Topo esquerdo
        if row == 0 and col == 0:
            if value in ['FC', 'FE']:
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            
            if value in ['VC', 'VE', 'VD']:
                if value == 'VB':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'VB'))
                return set(actions_list)
        
        # Topo direito
        elif row == 0 and col == self.dim - 1:
            if value in ['FC', 'FD']:
                actions_list.append((row, col, 'FE'))
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            
            if value in ['VC', 'VB', 'VD']:
                if value == 'VE':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'VE'))
                return set(actions_list)
            
        # Topo meio
        elif row == 0 and col not in [0, self.dim - 1]:
            if value == 'LV':
                if value == 'LH':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'LH'))
                return set(actions_list)
            
            if value in ['BE', 'BD', 'BC']:
                if value == 'BB':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'BB'))
                return set(actions_list)
            
            if value == 'FC':
                actions_list.append((row, col, 'FB'))
                actions_list.append((row, col, 'FE'))
                actions_list.append((row, col, 'FD'))
                return set(actions_list)

            if value in ['VC', 'VD']:
                actions_list.append((row, col, 'VB'))
                actions_list.append((row, col, 'VE'))
                return set(actions_list)
        
        # Baixo esquerdo
        elif row == self.dim - 1 and col == 0:
            if value in ['FB', 'FE']:
                actions_list.append((row, col, 'FC'))
                actions_list.append((row, col, 'FD'))
                return set(actions_list)
            
            if value in ['VC', 'VB', 'VE']:
                if value == 'VD':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'VD'))
                return set(actions_list)
            
        # Baixo direito
        elif row == self.dim - 1 and col == self.dim - 1:
            if value in ['FB', 'FD']:
                actions_list.append((row, col, 'FE'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            
            if value in ['VD', 'VB', 'VE']:
                if value == 'VC':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'VC'))
                return set(actions_list)
        
        # Meio baixo
        elif row == self.dim - 1 and col not in [0, self.dim - 1]:
            if value == 'LV':
                if value == 'LH':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'LH'))
                return set(actions_list)
            
            if value in ['BB', 'BE', 'BD']:
                if value == 'BC':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'BC'))
                return set(actions_list)
            
            if value == 'FB':
                actions_list.append((row, col, 'FC'))
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FE'))
                return set(actions_list)

            if value in ['VB', 'VE']:
                actions_list.append((row, col, 'VC'))
                actions_list.append((row, col, 'VD'))
                return set(actions_list)
        
        # Lateral esquerda
        elif row not in [0, self.dim - 1] and col == 0:
            if value == 'LH':
                if value == 'LV':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'LV'))
                return set(actions_list)
            
            if value == 'FE':
                actions_list.append((row, col, 'FC'))
                actions_list.append((row, col, 'FD'))
                actions_list.append((row, col, 'FB'))
                return set(actions_list)
            
            if value in ['BC', 'BB', 'BE']:
                if value == 'BD':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'BD'))
                return set(actions_list)
            
            if value in ['VC', 'VE']:
                actions_list.append((row, col, 'VB'))
                actions_list.append((row, col, 'VD'))
                return set(actions_list)
            
        # Lateral direita
        elif row not in [0, self.dim - 1] and col == self.dim - 1:
            if value == 'LH':
                if value == 'LV':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'LV'))
                return set(actions_list)
            
            if value == 'FD':
                actions_list.append((row, col, 'FE'))
                actions_list.append((row, col, 'FB'))
                actions_list.append((row, col, 'FC'))
                return set(actions_list)
            
            if value in ['BC', 'BB', 'BD']:
                if value == 'BE':
                    state.board.locked[(row, col)] = True
                else:
                  actions_list.append((row, col, 'BE'))
                return set(actions_list)
            
            if value in ['VB', 'VD']:
                actions_list.append((col, row, 'VC'))
                actions_list.append((col, row, 'VE'))
                return set(actions_list)
            
        return set(actions_list)
    
    def F_Actions(self, value, row, col):
        actions_list = []
          
        for rotation in self.rotations[value]:
            actions_list.append((row, col, rotation))

        return set(actions_list)
    
    # TODO: Fazer função que da lock logo no inicio

    def isBorder(self, row, col):
        return row == 0 or col == 0 or row == self.dim - 1 or col == self.dim - 1
        
    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
            
        actions_list = []

        for row in range(state.board.dim):
            for col in range(state.board.dim):
                value = state.board.get_value(row, col)                
                if not state.board.locked[(row, col)]:
                  if self.isBorder(row, col):
                    border_set = self.checkWrongBorderActions(value, row, col, state)
                    if len(border_set) == 0:
                        border_set = self.checkRightBorderActions(value, row, col)
                        actions_list.extend(list(border_set))
                    else:
                        actions_list.extend(list(border_set))
                  else:
                    border_set = self.F_Actions(value, row, col)
                    actions_list.extend(list(border_set))
                

                # ESTA NUM LOOP INFINITO NAO SEI PORQUE

                
       # random.shuffle(actions_list)   
        #print(actions_list)     
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
            print("----====----")
            new_Board.print_board()
            print("----====----")
            return PipeManiaState(new_Board)
        
        
        '''print("----====----")
        new_Board.print_board()
        print("----====----")'''

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
        "FD	BB	BB	FE",
        "FD	BE	FC	FB",
        "VB	BC	BB	BE",
        "FC	FD	VC	FC"
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