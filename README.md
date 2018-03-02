# Bane
A chat room with sprinkles.

# Features
* All users will connect to each other automatically.
  * Start a server by asking someone's 'Invite Code' (a compressed socket) and type '/invite [Invite Code]'.
  * All users who connect to one of you will connect with the rest of the users who are connected with you.
  * All connected users can communicate via the 'Global' chat room.

* Private chat ahoy!
  * Chat privately with a single user within a server.

# To-Do
* Make queueing system.
* Add the game.
* Allow people to challenge each other.
* Allow the game master to make their own rules.
* Multi-user private chat room.

# Bugs
* Sockets not properly being closed.
  * Possible fix it to make a connection test before finally setting the socket as the server.
* Users randomly crashing when attempting to connect to a server with more than 1 user.
  * Possibly a loop error with the ahoge.py persistent sender.
