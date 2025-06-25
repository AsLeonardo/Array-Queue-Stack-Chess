import tkinter as tk

# --- Configurações Globais ---
BOARD_SIZE    = 8   # dimensão do tabuleiro (8x8)
SQUARE_SIZE   = 80  # tamanho de cada casa em pixels
ANIM_STEPS    = 10  # quadros na animação
IMG_FOLDER    = "images"    # pasta das imagens das peças
PIECE_IMAGES  = {           # mapeamento de código de peça para arquivo de imagem
    'wp': 'wp.png', 'wn': 'wn.png', 'wb': 'wb.png',
    'wr': 'wr.png', 'wq': 'wq.png', 'wk': 'wk.png',
    'bp': 'bp.png', 'bn': 'bn.png', 'bb': 'bb.png',
    'br': 'br.png', 'bq': 'bq.png', 'bk': 'bk.png',
}

# --- Classes de Peça e Regras ---
class Piece:
    def __init__(self, color):
        self.color = color  # 'w' ou 'b'
    def moves(self, board, r, c):
        return []

class Pawn(Piece):
    def moves(self, board, r, c):
        dirs = -1 if self.color=='w' else 1
        res = []
        # avanço simples
        if board.empty(r+dirs, c):
            res.append((r+dirs, c))
            # avanço duplo se na linha inicial
            start = 6 if self.color=='w' else 1
            if r == start and board.empty(r+2*dirs, c):
                res.append((r+2*dirs, c))
        # capturas
        for dc in (-1,1):
            if board.enemy(r+dirs, c+dc, self.color):
                res.append((r+dirs, c+dc))
        return res

class Night(Piece):
    OFFSETS = [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]
    def moves(self, board, r, c):
        res = []
        for dr,dc in Night.OFFSETS:
            nr, nc = r+dr, c+dc
            # verifica validade e se não é amigável
            if board.valid(nr,nc) and not board.friendly(nr,nc,self.color):
                res.append((nr,nc))
        return res

class Bishop(Piece):
    def moves(self, board, r, c):
        # movimento deslizante em diagonais
        return board._sliding(r, c, self.color, [(1,1),(1,-1),(-1,1),(-1,-1)])

class Rook(Piece):
    def moves(self, board, r, c):
        # movimento deslizante em fileiras e colunas
        return board._sliding(r, c, self.color, [(1,0),(-1,0),(0,1),(0,-1)])

class Queen(Piece):
    def moves(self, board, r, c):
        # combinação de movimentos do bispo e torre
        return board._sliding(
            r, c, self.color,
            [(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
        )

class King(Piece):
    def moves(self, board, r, c):
        res = []
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==dc==0: continue
                nr, nc = r+dr, c+dc
                if board.valid(nr,nc) and not board.friendly(nr,nc,self.color):
                    res.append((nr,nc))
        return res

# --- Tabuleiro ---
class Board:
    def __init__(self, game):
        self.game = game
        # matriz de 8x8 usando lista de listas
        self.grid = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self._setup_initial()

    def _setup_initial(self):
        # inicializa posições de peões
        for c in range(BOARD_SIZE):
            self.grid[6][c] = Pawn('w')
            self.grid[1][c] = Pawn('b')
            # ordem das peças na primeira e última fileira
        order = [Rook, Night, Bishop, Queen, King, Bishop, Night, Rook]
        for c, cls in enumerate(order):
            self.grid[7][c] = cls('w')
            self.grid[0][c] = cls('b')

    def valid(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def empty(self, r, c):
        return self.valid(r, c) and self.grid[r][c] is None

    def friendly(self, r, c, color):
        return self.valid(r, c) and self.grid[r][c] and self.grid[r][c].color == color

    def enemy(self, r, c, color):
        return self.valid(r, c) and self.grid[r][c] and self.grid[r][c].color != color

    def _sliding(self, r, c, color, directions):
        res = []
        # percorre cada direção até encontrar obstáculo
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            while self.valid(nr, nc):
                if self.empty(nr, nc):
                    res.append((nr, nc))
                elif self.enemy(nr, nc, color):
                    res.append((nr, nc))
                    break
                else:
                    break
                nr += dr; nc += dc
        return res

# --- Lógica de Jogo e GUI ---
class Game:
    def __init__(self, canvas):
        self.canvas         = canvas
        self.board          = Board(self)
        self.images         = {}
        self._load_images()
        # FILA: lista usada em FIFO para alternar turnos
        self.turns          = ['w', 'b']   
        # PILHA: lista usada em LIFO para histórico de movimentos
        self.history        = []       
        # seleção atual e movimentos possíveis (LISTA dinâmica)    
        self.selected       = None
        self.possible_moves = []           

        self._draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def _load_images(self):
        for key, fn in PIECE_IMAGES.items():
            path = f"{IMG_FOLDER}/{fn}"
            try:
                self.images[key] = tk.PhotoImage(file=path)
            except tk.TclError:
                raise FileNotFoundError(f"Imagem não encontrada: {path}")

    def _draw_board(self):
        self.canvas.delete("all")
        # desenha casas alternadas
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
                color = "#EEE" if (r+c)%2 else "#555"
                self.canvas.create_rectangle(x0, y0, x0+SQUARE_SIZE, y0+SQUARE_SIZE,
                                             fill=color, outline="")
        # destaca seleção
        if self.selected:
            r, c = self.selected
            x0, y0 = c*SQUARE_SIZE, r*SQUARE_SIZE
            self.canvas.create_rectangle(x0, y0, x0+SQUARE_SIZE, y0+SQUARE_SIZE,
                                         outline="yellow", width=3)
         # destaca movimentos possíveis
        for (mr, mc) in self.possible_moves:
            x0, y0 = mc*SQUARE_SIZE, mr*SQUARE_SIZE
            self.canvas.create_rectangle(x0+5, y0+5, x0+SQUARE_SIZE-5, y0+SQUARE_SIZE-5,
                                         outline="cyan", width=2)
        # desenha peças no tabuleiro
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.board.grid[r][c]
                if p:
                    key = p.color + p.__class__.__name__[0].lower()
                    self.canvas.create_image(c*SQUARE_SIZE, r*SQUARE_SIZE,
                                             anchor="nw", image=self.images[key])

    def on_click(self, event):
        c = event.x // SQUARE_SIZE
        r = event.y // SQUARE_SIZE
        if not self.board.valid(r, c): return
        cur = self.turns[0] # jogador da vez (fila FIFO)
        p = self.board.grid[r][c]
        # seleção de peça
        if self.selected is None:
            if p and p.color == cur:
                self.selected = (r, c)
                self.possible_moves = p.moves(self.board, r, c)
        else:
            r0, c0 = self.selected
            piece = self.board.grid[r0][c0]
            if (r, c) in self.possible_moves:
                # empilha estado antes do movimento
                captured = self.board.grid[r][c]
                self.history.append((r0, c0, piece, r, c, captured))
                self._animate_move(r0, c0, r, c, piece)
                # atualiza posições no tabuleiro
                self.board.grid[r0][c0] = None
                self.board.grid[r][c]   = piece
                # pop(0) e append para alternar turnos
                self.turns.append(self.turns.pop(0))
                # verifica vitória
                if isinstance(captured, King):
                    self.show_victory(piece.color)
            self.selected = None
            self.possible_moves = []
        self._draw_board()

    def _animate_move(self, r0, c0, r1, c1, piece):
        key = piece.color + piece.__class__.__name__[0].lower()
        img_obj = None
        for obj in self.canvas.find_all():
            if self.canvas.type(obj) == "image":
                x, y = self.canvas.coords(obj)
                if (round(y)//SQUARE_SIZE, round(x)//SQUARE_SIZE) == (r0, c0):
                    img_obj = obj
                    break
        if not img_obj: return
        dx = (c1 - c0)*SQUARE_SIZE/ANIM_STEPS
        dy = (r1 - r0)*SQUARE_SIZE/ANIM_STEPS
        def step(count=0):
            if count < ANIM_STEPS:
                self.canvas.move(img_obj, dx, dy)
                self.canvas.after(30, lambda: step(count+1))
        step()

    def undo(self):
        if not self.history: return
        # desempilha último movimento
        r0, c0, piece, r1, c1, captured = self.history.pop()
        self.board.grid[r0][c0] = piece
        self.board.grid[r1][c1] = captured
        # retorna jogador anterior à frente da fila
        self.turns.insert(0, self.turns.pop())
        self.selected = None
        self.possible_moves = []
        self._draw_board()

    def show_victory(self, winner):
        win = tk.Toplevel()
        win.title("Vitória!")
        msg = "Jogador Branco venceu!" if winner == 'w' else "Jogador Preto venceu!"
        label = tk.Label(win, text=msg, font=(None, 16))
        label.pack(padx=20, pady=10)
        btn = tk.Button(win, text="Recomeçar", command=lambda: self.restart(win))
        btn.pack(pady=(0,20))

    def restart(self, win_window):
        # fecha janela de vitória
        win_window.destroy()
        # reinicializa components do jogo
        self.board = Board(self)
        self.turns = ['w','b']
        self.history = []
        self.selected = None
        self.possible_moves = []
        self._draw_board()

# --- Início da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Xadrez – Python Tkinter com Tela de Vitória")
    canvas = tk.Canvas(root, width=SQUARE_SIZE*BOARD_SIZE,
                       height=SQUARE_SIZE*BOARD_SIZE)
    canvas.pack()
    game = Game(canvas)
    root.bind("<Control-z>", lambda e: game.undo())
    root.mainloop()
