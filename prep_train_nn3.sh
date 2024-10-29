cd pencil-prep
python3 train_priv_server.py -p agnews_cnn -n 0 -C 8 -o SGD -om 0.8 -lr 0.01 > /dev/null &
sleep 5
python3 train_priv_client.py -s None -e 10 > logs/train_nn3.log &
cd ..
