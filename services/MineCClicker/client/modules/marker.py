from enum import Enum

class Marker(Enum):
	
	COVERED = None
	RED = -3
	FLAG = -2
	BOMB = -1
	EMPTY = 0
	# Numbers from 1 to 8 are the number of bombs in the adjacent cells

	@staticmethod
	def values():
		return [ marker.value for marker in Marker ]
