import time
import struct

from enum import Enum

from .marker import Marker

class Network():

	class ReqType(Enum):
		SIGNUP = 0
		LOGIN = 1
		CREATE_BOARD = 2
		LOAD_BOARD = 3
		PLAY = 4
		UNCOVER = 5
		CHECK_WIN = 6
		QUIT = 7


	class ReqHdr():
		def __init__(self, type, len):
			self.ts = int(time.time())
			self.type = type.value
			self.len = len
		
		@property
		def bytes(self):
			return struct.pack('<IBH', self.ts, self.type, self.len)
		
		@property
		def size(self):
			return len(self.bytes)


	class Str():
		def __init__(self, data):
			self.data = data if isinstance(data, bytes) else data.encode()

		@property
		def bytes(self):
			return struct.pack('<B', len(self.data)) + self.data
		
		@property
		def size(self):
			return len(self.bytes)


	class Board():
		def __init__(self, board):
			self.board = board

		@property
		def bytes(self):
			cells = [cell for row in self.board for cell in row]
			bs = [0] * ((len(cells) + 7) // 8)
			for i, cell in enumerate(cells):
				if cell == Marker.FLAG:
					bs[i // 8] |= 1 << (i  % 8)
			return struct.pack('<Q', len(self.board)) + bytes(bs)

		@property
		def size(self):
			return len(self.bytes)


	@staticmethod
	def recv(conn, size):
		data = b''
		while size != 0:
			chunk = conn.recv(size)
			if not chunk:
				raise EOFError('connection closed by server (timeout?)')
			data += chunk
			size -= len(chunk)
		return data


	@staticmethod
	def proto_get_u8(conn):
		return struct.unpack('<B', Network.recv(conn, 1))[0]


	@staticmethod
	def proto_get_u64(conn):
		return struct.unpack('<Q', Network.recv(conn, 8))[0]


	@staticmethod
	def proto_get_i8(conn):
		return struct.unpack('<b', Network.recv(conn, 1))[0]


	@staticmethod
	def proto_get_str(conn):
		size = Network.proto_get_u8(conn)
		return Network.recv(conn, size).rstrip(b'\x00').decode()


	@staticmethod
	def net_send_req(conn, type, data):
		hdr = Network.ReqHdr(type, len(data))
		req = hdr.bytes + data
		conn.sendall(req)


	@staticmethod
	def net_get_reply_hdr(conn):
		res = Network.proto_get_u8(conn)
		if res:
			return res, None
		msg = Network.proto_get_str(conn)
		return res, msg


	@staticmethod
	def net_get_reply_play(conn):
		res, msg = Network.net_get_reply_hdr(conn)
		if not res:
			return res, msg
		game_seed = Network.proto_get_u64(conn)
		board_dim = Network.proto_get_u64(conn)
		num_bombs = Network.proto_get_u64(conn)
		return res, (game_seed, board_dim, num_bombs)


	@staticmethod
	def net_get_reply_uncover(conn):
		res, msg = Network.net_get_reply_hdr(conn)
		if not res:
			return res, msg
		content = Network.proto_get_i8(conn)
		board = None
		if content == -1:
			dim = Network.proto_get_u64(conn)
			raw_cells = Network.recv(conn, (dim*dim + 7) // 8)
			
			board = [ [ 0 for _ in range(dim) ] for _ in range(dim) ]
			for row in range(dim):
				for col in range(dim):
					off = row * dim + col
					board[row][col] = Marker.BOMB if raw_cells[off // 8] & (1 << (off % 8)) else Marker.EMPTY

		return res, (content, board)


	@staticmethod
	def net_get_reply_check_win(conn):
		res, msg = Network.net_get_reply_hdr(conn)
		if not res:
			return res, msg
		string = Network.proto_get_str(conn)
		return res, string
