#!/bin/bash
source /home/baadalvm/anaconda3/bin/activate $1 
javac Chachu20.java
java Chachu20 $2
python3 deploy_model.py $2
