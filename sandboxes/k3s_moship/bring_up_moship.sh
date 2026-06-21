# 1. Clean out the legacy testing namespace entirely
kubectl delete namespace edge-stack --ignore-not-found=true

# 2. Establish the operational namespace baseline
kubectl create namespace edge-stack

# 3. Dynamic Script Read: Convert the local Python file into a secure cluster configuration store
kubectl create configmap python-source-code --from-file=main.py -n edge-stack

# 4. Dynamic Script Read: Convert your local Nginx proxy routing file into a cluster config store
kubectl create configmap nginx-proxy-config --from-file=default.conf -n edge-stack

# 5. Bring up the physical decoupled cluster topology
kubectl apply -f cluster-topology.yaml


kubectl get pods -n edge-stack -o wide --watch