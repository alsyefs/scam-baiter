from flask_socketio import SocketIO, emit, join_room, leave_room, send, disconnect
# from flask_sockets import Sockets
from flask_sock import Sock

socketio = SocketIO()
sock = Sock()
# sockets = Sockets()