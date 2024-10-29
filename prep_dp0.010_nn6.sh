cd pencil-prep
python3 train_priv_server.py -p resnet50_classifier -n 0.01 -C 8 -o SGD -om 0.8 -lr 0.01 > /dev/null &
sleep 5
python3 train_priv_client.py -s None -e 10 > logs/dp0.010_nn6.log &
cd ..
