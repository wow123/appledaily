echo Who am i:
whoami
echo Current dir:
pwd
echo DISPLAY=$DISPLAY
echo PATH=$PATH
echo HOME=$HOME
echo APPLEDAILY_HOME=$APPLEDAILY_HOME
rm $APPLEDAILY_HOME/tmp/*
echo "tmp directory cleared."
date
python3 $APPLEDAILY_HOME/main.py
date
