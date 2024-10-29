cd pencil-prep
python3 server_costs.py -p cifar10_sphinx > logs/costs_nn4.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
