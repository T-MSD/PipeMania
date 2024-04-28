# pipe.py: Template para implementação do projeto de Inteligência Artificial 2023/2024.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 102613 Tiago Miguel Santos Dias
# 103037 Tiago Coutinho Carreto Tavares Rebelo

import sys
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

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


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

        board = []
        for row in sys.stdin.readlines():
            row = row.strip().split("\t")
            board.append(row)
            
        return Board(board)

    # TODO: outros metodos da classe
    def print_board(self):
        for row in self.board:
            print(row)

class PipeMania(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        self.state = PipeManiaState(board)

    def actions(self, state: PipeManiaState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        
        actions = []
        
        # TODO
        
        pass
        
    def result(self, state: PipeManiaState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: PipeManiaState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema.""" 
        
        above = ["FC", "BC", "BE", "BD", "VC", "VD", "LV"]
        under = ["FB", "BB", "BE", "BD", "VB", "VE", "LV"]
        AtRight = ["FD", "BD", "BC", "BB", "VD", "VB", "LH"]
        AtLeft = ["FE", "BE", "BC", "BB", "VE", "VC", "LH"]
        
        for row in range(state.board.dim):
            for col in range(state.board.dim):
                value = state.board.get_value(row, col)
                              
                print(value)
                
                up, down = state.board.adjacent_vertical_values(row, col)
                left, right = state.board.adjacent_horizontal_values(row, col)
                
                if value == "FB":
                    if down not in above:
                        return False

                if value == "FC":
                    if up not in under:
                        return False
                    
                if value == "FE":
                    if left not in AtRight:
                        return False
                    
                if value == "FD":
                    if right not in AtLeft:
                        return False
                    
                if value == "BB":
                    if down not in above or right not in AtLeft or left not in AtRight:
                        return False
                    
                if value == "BC":
                    if up not in under or right not in AtLeft or left not in AtRight:
                        return False
                
                if value == "BE":
                    if up not in under or down not in under or left not in AtRight:
                        return False
                    
                if value == "BD":
                    if up not in down or right not in AtLeft or right not in AtLeft:
                        return False
                    
                if value == "VC":
                    if up not in under or left not in AtRight:
                        return False
                    
                if value == "VB":
                    print(down)
                    print(right)
                    if down not in above or right not in AtLeft:
                        return False
                    
                if value == "VE":
                    if down not in above or left not in AtRight:
                        return False
                    
                if value == "VD":
                    if up not in under or right not in AtLeft:
                        return False
                    
                if value == "LH":
                    if right not in AtLeft or left not in AtRight:
                        return False
                    
                if value == "LH":
                    if up not in under or down not in above:
                        return False

                    
    
        return True

        


        

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    board = Board.parse_instance()
    board.print_board()

    problem = PipeMania(board)
    print(problem.goal_test(problem.state))
    
    #print(board.get_value(0,0))
    
    #print(board.adjacent_vertical_values(0, 0))
    #print(board.adjacent_horizontal_values(0, 0))
    #print(board.adjacent_vertical_values(1, 1))
    #print(board.adjacent_horizontal_values(1, 1))
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.
