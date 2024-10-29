cd pencil-fullhe
for test in 1 2 3; do
    python3 train_priv_server.py -p mnist_aby3 -n 0.02 -C 8 -o SGD -om 0.8 -lr 0.01 > /dev/null &
    sleep 5
    python3 train_priv_client.py -s 4:0 -e 10 > logs/train_nn1_1024_${test}.log
    sleep 30
done
cd ..

cd pencil-prep
for test in 1 2 3; do
    python3 train_priv_server.py -p mnist_aby3 -n 0.02 -C 8 -o SGD -om 0.8 -lr 0.01 > /dev/null &
    sleep 5
    python3 train_priv_client.py -s 4:0 -e 10 > logs/train_nn1_1024_${test}.log
    sleep 30
done
cd ..


