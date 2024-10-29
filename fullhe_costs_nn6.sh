cd pencil-fullhe
python3 server_costs.py -p resnet50_classifier > logs/costs_nn6.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
