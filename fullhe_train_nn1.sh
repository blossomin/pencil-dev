# cd pencil-fullhe
# for bs in 64; do
#     cp model.temp model.py
#     sed -i "s/(BATCHSIZE, 3, 32, 32)/(${bs}, 3, 32, 32)/g" model.py
#     for test in 1 2 3; do
#         python3 train_priv_server.py -p cifar10_sphinx -n 0.02 -C 8 -o SGD -om 0.8 -lr 0.01 > logs/train_cpu_nn4_server_${bs}_${test}.log 2>&1 &
#         sleep 5
#         python3 train_priv_client.py -s 4:0 -e 10 > logs/train_cpu_nn4_client_${bs}_${test}.log 2>&1
#         sleep 30
#     done
# done
cd pencil-prep
for bs in 64 256 1024; do
    cp model.temp model.py
    sed -i "s/(BATCHSIZE, 1, 28, 28)/(${bs}, 1, 28, 28)/g" model.py
    for test in 1 2 3; do
        python3 train_priv_server.py -p mnist_aby3 -n 0.02 -C 8 -o SGD -om 0.8 -lr 0.01 > logs/train_cpu_nn1_server_${bs}_${test}.log 2>&1 &
        sleep 5
        python3 train_priv_client.py -s 4:0 -e 10 > logs/train_cpu_nn1_client_${bs}_${test}.log 2>&1
        sleep 30
    done
done
cd ..


