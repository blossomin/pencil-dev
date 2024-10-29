cd pencil-fullhe
python3 server_costs.py -p agnews_cnn > logs/costs_nn3.log &
sleep 5
python3 client_costs.py > /dev/null &
cd ..
