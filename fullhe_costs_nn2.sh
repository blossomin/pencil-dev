cd pencil-fullhe
python3 server_costs.py -p mnist_chameleon > logs/costs_nn2.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
