!!!!!!!!!!!!!!!!!!!WARNING!!!!!!!!!!!!!!!!!!!   
This chain is still under construction.   
First install python 3.11   
then:
```
python3.11 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install flask
pip install flask
pip install requests
```
Create a peers.txt file
Enter the IP address of your node and the port you will be using. Do not enter blank lines or press enter otherwise you will get error.
```
http://<Your IP>:<Your Port>/<Your endpoint where blocks are stored>
http://192.168.12.56:5000/blocks
```
Note this IP is only a place holder.

Important Note:
`blocks` folder needs to be created, before starting the chain.
