python train_priv_server.py > server_1.log 2>&1 &
sleep 3
python train_priv_client.py  > client_1.log 2>&1