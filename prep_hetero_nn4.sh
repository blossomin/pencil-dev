cd pencil-prep
python3 train_priv_server.py -p cifar10_sphinx -n 0 -C 8 -o SGD -om 0.8 -lr 0.01 > /dev/null &
sleep 5
python3 train_priv_client.py -s 5:5 -e 10 > logs/hetero_nn4.log &
cd ..
