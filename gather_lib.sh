for x in ./OpenCheetah/build/lib/libgemini.so \
    ./OpenCheetah/build/deps/emp-tool/libemp-tool.so \
    ./seal-cuda/build/src/libtroy.so \
    ./seal-cuda/build/pytroy.cpython-310-x86_64-linux-gnu.so \
    ./EzPC/SCI/build/lib/sci_provider_alice.cpython-310-x86_64-linux-gnu.so \
    ./EzPC/SCI/build/lib/sci_provider_bob.cpython-310-x86_64-linux-gnu.so \
    ./OpenCheetah/build/lib/cheetah_provider_alice.cpython-310-x86_64-linux-gnu.so \
    ./OpenCheetah/build/lib/cheetah_provider_bob.cpython-310-x86_64-linux-gnu.so
do  
    echo $x 
    cp $x ./newlib/
done