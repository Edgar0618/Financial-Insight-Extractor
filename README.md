# COP4521-Project

Instructions to run:
1) On your terminal, run the commands:
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb/brew/mongodb-community

2) On the project root directory:
Install flask: pip install flask
Install pymongo: pip3 install pymongo 

3) Optional:
Install mongosh: brew install mongosh 
To run: mongosh
This lets you see important info about database such as the users registered.
Once you run mongosh, run: use("userDatabase")
This is our projects database
You can run a command such as: db.users.find({}, { password: 0, _id: 0 }) 
(shows you registered users)