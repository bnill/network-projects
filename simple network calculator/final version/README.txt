HIGH LEVEL APPROACH
1.Wrap the socket with SSL protocol to enable the SSL connections.
2.Considering multiple ways to identify the error input.
3.Using the speciality of Python to simplify calculations.
4.Using try and except when dealing with the connection errors.

CHALLENGES FACED
1.Received messy code when doing ssl connections. Problem solved by wrapping socket.
2.Failed to connect to the server at home. Problem solved by using vpn of NEU.
3.Fail at first to verify whether the port number is valid. Problem solved by scanning the document of Python to find s.isdigit()

TESTCASE SCENARIOS

Positive scenarios
./client.py -p 27994 -s cs5700f16.ccs.neu.edu 001664011
./client.py -p 27993 cs5700f16.ccs.neu.edu 001664011
./client.py -s cs5700f16.ccs.neu.edu 001664011
./client.py cs5700f16.ccs.neu.edu 001664011

Negative scenarios
./client.py -p 9889946 -s cs5700f16.ccs.neu.edu 001664011
./client.py -p 9595952 cs5700f16.ccs.neu.edu 001664011
./client.py -p abcdef -s cs5700f16.ccs.neu.edu 001664011
./client.py -p wxyzab cs5700f16.ccs.neu.edu 001664011
./client.py -p 27993 cs5700f16.ccs.neu.edu 45487
./client.py abcdefghij3
./client.py -p 27993 cs5700f16.ccs.neu.edu 001664011 001284143
