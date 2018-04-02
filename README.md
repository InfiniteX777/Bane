# Sparrow
A chat room with sprinkles.

# Features
* All users will connect to each other automatically.
  * Start a server by asking someone's 'Invite Code' (a compressed socket) and type '/invite [Invite Code]'.
  * All users who connect to one of you will connect with the rest of the users who are connected with you.
  * All connected users can communicate via the 'Global' chat room.

* Private chat ahoy!
  * Chat privately with a single user within a server.
  * Click the user you want to chat with on the right-side of your screen.

* Host a room for your buddies!
  * Create the room by typing '/host [Room Name]' in any selected room.
  * There SHOULD NOT be any whitespaces or '\' characters in the room name!
  * Invite a buddy via '/invite [Invite Code]' in the selected room.
  * Only you and your buddies can see what's in the room.
  * Adding a password will allow players to join ('/host [Room Name] [Password]').
    * '/join [Password]' will allow players to join if the given password is correct.
    * You can still invite players in the room, allowing them to join without knowing the password.

* Send files!
  * Just type '/send' in a room and a file chooser dialog will appear.
  * Everybody in that room will receive the file.

* DU-DU-DU-DUEL!
  * Fight people directly via '/duel [Invite Code]'!

* Need help?
  * Type '/help' or '/commands' to see what you can do in the app!

# To-Do
* Make queueing system.
* Add the game.
* Allow people to challenge each other.
* Allow the game master to make their own rules.
