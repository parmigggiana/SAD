import struct
import socket

from .network import Network


class Client():
    def __init__(self, host, port):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((host, port))


    # Signup user
    def signup(self, username, password):
        username = Network.Str(username)
        password = Network.Str(password)
        data = username.bytes + password.bytes
        Network.net_send_req(self.conn, Network.ReqType.SIGNUP, data)

        success, res = Network.net_get_reply_hdr(self.conn)
        return success, res

    
    # Login user
    def login(self, username, password):
        username = Network.Str(username)
        password = Network.Str(password)
        data = username.bytes + password.bytes
        Network.net_send_req(self.conn, Network.ReqType.LOGIN, data)

        success, res = Network.net_get_reply_hdr(self.conn)
        return success, res

    
    # Create new board
    def create_board(self, name, secret, seed, board_dim, num_bombs):
        name = Network.Str(name)
        secret = Network.Str(secret)
        seed = struct.pack('<Q', seed)
        board_dim = struct.pack('<Q', board_dim)
        num_bombs = struct.pack('<Q', num_bombs)
        data = name.bytes + secret.bytes + seed + board_dim + num_bombs
        Network.net_send_req(self.conn, Network.ReqType.CREATE_BOARD, data)

        success, res = Network.net_get_reply_hdr(self.conn)
        return success, res
    
    
    # Load existing board
    def load_board(self, name):
        name = Network.Str(name)
        data = name.bytes
        Network.net_send_req(self.conn, Network.ReqType.LOAD_BOARD, data)

        success, res = Network.net_get_reply_hdr(self.conn)
        return success, res

    
    # Play game
    def play(self):
        Network.net_send_req(self.conn, Network.ReqType.PLAY, b"")

        success, res = Network.net_get_reply_play(self.conn)
        return success, res

    
    # Uncover cell
    def uncover(self, row, col):
        data = struct.pack('<BB', row, col)
        Network.net_send_req(self.conn, Network.ReqType.UNCOVER, data)

        success, res = Network.net_get_reply_uncover(self.conn)
        return success, res

    
    # Check win
    def check_win(self, board):
        data = Network.Board(board).bytes
        Network.net_send_req(self.conn, Network.ReqType.CHECK_WIN, data)

        success, res = Network.net_get_reply_check_win(self.conn)       
        return success, res

    def quit(self):
        Network.net_send_req(self.conn, Network.ReqType.QUIT, b"")

        success, res = Network.net_get_reply_hdr(self.conn)
        self.conn.close()
