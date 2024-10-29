cd pencil-fullhe
python3 server_costs.py -p mnist_aby3 > logs/costs_nn1.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
